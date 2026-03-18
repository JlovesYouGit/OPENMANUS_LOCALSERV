"""
brain_mesh_processor.py

Updated implementation: integrates descent-stage logic directly into per-bit-array processing.
- Adds MeshChunk.load_brain_core for optimized loading of yU/yD/XR/XL axis arrays.
- Adds mass model loader and shock-absorber application.
- Adds cancel_half_bank utility.
- Implements process_descent_bitarrays: applies three-stage descent profile directly to decoded
  2-bit-per-vertex arrays (deltas and flips) and updates zone vertex arrays in-place.

This file overwrites the previous prototype to provide a single cohesive implementation.
"""

from __future__ import annotations
import argparse
import math
import os
import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np

# ----------------------------- Utilities ------------------------------------

def now():
    return time.time()


def clamp(v, a, b):
    return max(a, min(b, v))


# -------------------------- Mesh chunk loader -------------------------------

@dataclass
class MeshChunk:
    vertices: np.ndarray
    indices: np.ndarray
    id: Optional[int] = None
    attrs: Optional[Dict[str, np.ndarray]] = None

    @staticmethod
    def load_from_npy(vertex_path: str, index_path: Optional[str] = None) -> "MeshChunk":
        if vertex_path.endswith('.npz'):
            npz = np.load(vertex_path)
            v = npz['vertices'] if 'vertices' in npz else npz[npz.files[0]]
            if 'indices' in npz:
                i = npz['indices']
            elif index_path:
                i = np.load(index_path)
            else:
                raise ValueError('npz file missing indices; provide index_path')
        else:
            v = np.load(vertex_path)
            if index_path:
                i = np.load(index_path)
            else:
                raise ValueError('index_path required for separate files')
        return MeshChunk(vertices=v.astype(np.float32), indices=i.astype(np.int32), attrs={})

    @staticmethod
    def load_brain_core(source: str | os.PathLike | dict, axis_names: Optional[List[str]] = None, allow_mmap: bool = True) -> "MeshChunk":
        """
        Optimized loader for brain core mesh and axis sequences (yU, yD, XR, XL).
        Accepts dict, .npz file, directory with .npy files, or vertices.npy with companion indices file.
        Returns MeshChunk with attrs for any axis arrays found.
        """
        if axis_names is None:
            axis_names = ["yU", "yD", "XR", "XL"]

        def try_get(mapping, keys):
            for k in keys:
                if k in mapping:
                    return mapping[k]
            return None

        attrs: Dict[str, np.ndarray] = {}

        if isinstance(source, dict):
            src = source
            v = try_get(src, ["vertices", "verts", "v", "positions"])
            i = try_get(src, ["indices", "faces", "tris", "connectivity"])
            if v is None or i is None:
                raise ValueError('Source dict must contain vertices and indices')
            vertices = np.asarray(v, dtype=np.float32)
            indices = np.asarray(i, dtype=np.int32)
            for name in axis_names:
                if name in src:
                    attrs[name] = np.asarray(src[name])
            return MeshChunk(vertices=vertices, indices=indices, attrs=attrs)

        sp = os.fspath(source)
        if os.path.isdir(sp):
            vp = os.path.join(sp, 'vertices.npy')
            ip = os.path.join(sp, 'indices.npy')
            if not os.path.exists(vp) or not os.path.exists(ip):
                raise ValueError('Directory must contain vertices.npy and indices.npy')
            vertices = np.load(vp, mmap_mode='r' if allow_mmap else None).astype(np.float32)
            indices = np.load(ip, mmap_mode='r' if allow_mmap else None).astype(np.int32)
            for name in axis_names:
                ap = os.path.join(sp, f"{name}.npy")
                if os.path.exists(ap):
                    attrs[name] = np.load(ap, mmap_mode='r' if allow_mmap else None)
            return MeshChunk(vertices=vertices, indices=indices, attrs=attrs)

        if sp.endswith('.npz'):
            npz = np.load(sp, mmap_mode='r' if allow_mmap else None)
            v = try_get(npz, ["vertices", "verts", "v", "positions"])
            i = try_get(npz, ["indices", "faces", "tris", "connectivity"])
            if v is None or i is None:
                files = list(npz.files)
                if len(files) >= 2:
                    v = npz[files[0]]
                    i = npz[files[1]]
                else:
                    raise ValueError('npz must contain vertices and indices')
            vertices = np.asarray(v, dtype=np.float32)
            indices = np.asarray(i, dtype=np.int32)
            for name in axis_names:
                if name in npz:
                    attrs[name] = np.asarray(npz[name])
            return MeshChunk(vertices=vertices, indices=indices, attrs=attrs)

        base, ext = os.path.splitext(sp)
        if ext == '.npy':
            candidate_indices = base + '_indices.npy'
            if not os.path.exists(candidate_indices):
                candidate_indices = base.replace('_vertices', '_indices') + '.npy'
            if not os.path.exists(candidate_indices):
                raise ValueError('Could not locate matching indices file for provided .npy')
            vertices = np.load(sp, mmap_mode='r' if allow_mmap else None).astype(np.float32)
            indices = np.load(candidate_indices, mmap_mode='r' if allow_mmap else None).astype(np.int32)
            return MeshChunk(vertices=vertices, indices=indices, attrs=attrs)

        raise ValueError('Unsupported source for load_brain_core')


# --------------------------- Bitstream decoder ------------------------------

class BitstreamDecoder:
    """Decode compact 2-bit-per-entry bitstreams with inversion masks and +2 semantics.
    Returns both deltas and flip flags plus the expanded raw 2-bit codes when needed.
    """

    def __init__(self, count: int):
        self.count = count

    def decode_bytes(self, data: bytes, invert_mask: Optional[bytes] = None) -> Tuple[np.ndarray, Optional[np.ndarray], np.ndarray]:
        packed_len = (self.count + 3) // 4
        if len(data) < packed_len:
            raise ValueError(f'Packed bitstream too short; need {packed_len} bytes')
        raw = np.frombuffer(data[:packed_len], dtype=np.uint8)
        a0 = raw & 0x03
        a1 = (raw >> 2) & 0x03
        a2 = (raw >> 4) & 0x03
        a3 = (raw >> 6) & 0x03
        expanded = np.empty(packed_len * 4, dtype=np.uint8)
        expanded[0::4] = a0
        expanded[1::4] = a1
        expanded[2::4] = a2
        expanded[3::4] = a3
        expanded = expanded[: self.count]

        deltas = np.zeros(self.count, dtype=np.uint8)
        flips = np.zeros(self.count, dtype=np.bool_) if expanded.max() == 3 else None

        if flips is None:
            deltas[:] = expanded
        else:
            mask1 = expanded == 1
            mask2 = expanded == 2
            maskf = expanded == 3
            deltas[mask1] = 1
            deltas[mask2] = 2
            flips[maskf] = True

        if invert_mask is not None:
            bmask = np.frombuffer(invert_mask, dtype=np.uint8)
            bit_expanded = np.unpackbits(bmask, bitorder='little')[: self.count].astype(bool)
            if flips is None:
                flips = bit_expanded
            else:
                flips ^= bit_expanded

        return deltas, flips, expanded


# ----------------------- Orientation table & caching ------------------------

@dataclass
class Orientation:
    mat: np.ndarray
    name: str = ""


class OrientationTable:
    def __init__(self):
        self._table: Dict[str, Orientation] = {}
        self._cache: Dict[Tuple[str, ...], np.ndarray] = {}
        self._lock = threading.Lock()
        I = np.eye(3, dtype=np.float32)
        self._table['I'] = Orientation(mat=I, name='I')

    def add(self, name: str, mat: np.ndarray):
        assert mat.shape == (3, 3)
        self._table[name] = Orientation(mat=mat.astype(np.float32), name=name)

    def compose(self, names: List[str]) -> np.ndarray:
        key = tuple(names)
        with self._lock:
            if key in self._cache:
                return self._cache[key]
        mat = np.eye(3, dtype=np.float32)
        for n in names:
            mat = mat.dot(self._table[n].mat)
        with self._lock:
            self._cache[key] = mat
        return mat


# ------------------------------- Zone --------------------------------------

@dataclass
class Zone:
    id: int
    bbox_min: np.ndarray
    bbox_max: np.ndarray
    chunk: MeshChunk
    bitstream: Optional[bytes] = None
    invert_mask: Optional[bytes] = None
    transform_names: List[str] = field(default_factory=lambda: ['I'])
    frozen: bool = False
    cache_vertices: Optional[np.ndarray] = None
    cache_version: int = 0


# ---------------------------- Untangle heuristic ---------------------------

# keep simple local_untangle (same as before)

def crossing_score_for_vertex(v_idx: int, verts: np.ndarray, indices: np.ndarray, neighborhood: List[int]) -> int:
    p = verts[:, :2]
    touched_edges = []
    for tri in indices:
        if v_idx in tri:
            other = [x for x in tri if x != v_idx]
            if len(other) == 2:
                touched_edges.append((v_idx, other[0]))
                touched_edges.append((v_idx, other[1]))
    def seg_cross(a1, a2, b1, b2):
        def orient(a, b, c):
            return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
        oa = orient(a1, a2, b1)
        ob = orient(a1, a2, b2)
        oc = orient(b1, b2, a1)
        od = orient(b1, b2, a2)
        return oa * ob < 0 and oc * od < 0

    score = 0
    for i in range(len(touched_edges)):
        a1 = p[touched_edges[i][0]]
        a2 = p[touched_edges[i][1]]
        for j in range(i + 1, len(touched_edges)):
            b1 = p[touched_edges[j][0]]
            b2 = p[touched_edges[j][1]]
            if seg_cross(a1, a2, b1, b2):
                score += 1
    return score


def local_untangle(verts: np.ndarray, indices: np.ndarray, max_iters: int = 5):
    n = len(verts)
    for it in range(max_iters):
        changed = False
        for v in range(n):
            orig = verts[v].copy()
            best = orig
            base_score = crossing_score_for_vertex(v, verts, indices, [])
            radius = 0.5 * (0.5 ** it)
            for ang in np.linspace(0, 2 * math.pi, 8, endpoint=False):
                delta = np.array([math.cos(ang) * radius, math.sin(ang) * radius, 0.0], dtype=np.float32)
                verts[v] = orig + delta
                sc = crossing_score_for_vertex(v, verts, indices, [])
                if sc < base_score:
                    base_score = sc
                    best = verts[v].copy()
                    changed = True
            verts[v] = best
        if not changed:
            break


# ------------------------- Processor orchestration -------------------------

class BrainMeshProcessor:
    def __init__(self, global_mesh: MeshChunk, zone_size: float = 10.0, n_workers: int = 4):
        self.mesh = global_mesh
        self.zone_size = float(zone_size)
        self.orientation_table = OrientationTable()
        self.zones: List[Zone] = []
        self._build_zones()
        self.decoder = BitstreamDecoder(count=len(global_mesh.vertices))
        self._version = 1
        self._lock = threading.Lock()
        self.n_workers = max(1, int(n_workers))
        self.telemetry = {"decode_time": 0.0, "transform_time": 0.0, "untangle_time": 0.0}

    def _build_zones(self):
        v = self.mesh.vertices
        bbox_min = v.min(axis=0)
        bbox_max = v.max(axis=0)
        spans = bbox_max - bbox_min
        nx = max(1, int(math.ceil(spans[0] / self.zone_size)))
        ny = max(1, int(math.ceil(spans[1] / self.zone_size)))
        nz = max(1, int(math.ceil(spans[2] / self.zone_size)))
        zone_id = 0
        for ix in range(nx):
            for iy in range(ny):
                for iz in range(nz):
                    min_corner = bbox_min + np.array([ix, iy, iz], dtype=np.float32) * self.zone_size
                    max_corner = min_corner + np.array([1.0, 1.0, 1.0], dtype=np.float32) * self.zone_size
                    z = Zone(id=zone_id, bbox_min=min_corner, bbox_max=max_corner, chunk=self.mesh)
                    z.bitstream = b'\x00' * ((len(self.mesh.vertices) + 3) // 4)
                    z.invert_mask = None
                    z.transform_names = ['I']
                    z.frozen = False
                    self.zones.append(z)
                    zone_id += 1

    def register_orientation(self, name: str, mat: np.ndarray):
        self.orientation_table.add(name, mat)

    def set_zone_bitstream(self, zone_id: int, packed_bitstream: bytes, invert_mask: Optional[bytes] = None):
        z = self.zones[zone_id]
        z.bitstream = packed_bitstream
        z.invert_mask = invert_mask

    def set_zone_transform(self, zone_id: int, transform_names: List[str]):
        z = self.zones[zone_id]
        z.transform_names = transform_names

    def freeze_zone(self, zone_id: int):
        self.zones[zone_id].frozen = True

    def unfreeze_zone(self, zone_id: int):
        self.zones[zone_id].frozen = False

    def _apply_transform_with_cache(self, zone: Zone) -> np.ndarray:
        start = now()
        mat = self.orientation_table.compose(zone.transform_names)
        with self._lock:
            if zone.cache_vertices is not None and zone.cache_version == self._version:
                self.telemetry['transform_time'] += now() - start
                return zone.cache_vertices
        verts = zone.chunk.vertices
        transformed = verts.dot(mat.T).astype(np.float32)
        with self._lock:
            zone.cache_vertices = transformed
            zone.cache_version = self._version
        self.telemetry['transform_time'] += now() - start
        return transformed

    def process_descent_bitarrays(self, zone: Zone, deltas: np.ndarray, flips: Optional[np.ndarray], expanded_codes: np.ndarray, mass_model: Optional[Dict] = None, params: Optional[Dict] = None) -> Dict:
        """
        Core per-bit-array processing implementing descent logic directly.

        - deltas: uint8 array of 0/1/2 values (length = vertex count)
        - flips: optional boolean array indicating flip codes
        - expanded_codes: raw 2-bit codes (0..3) per-vertex

        Descent stages:
          Start: +66 upward, 1 bar (ultra-stable)
          Mid:   06 apex, 2 bars (standard)
          Final: -56 locked, 2 bars (stable)

        We map the 2-bit codes into stage-specific operations and apply them vectorized to zone.cache_vertices.
        """
        if params is None:
            params = {}
        if mass_model is None:
            mass_model = {'M': 1.0}
        M = float(mass_model.get('M', 1.0))
        I = float(mass_model.get('I', 0.0)) if 'I' in mass_model else None

        # stage weights (bars -> damping mapping)
        def bars_to_w(b):
            return clamp(b * 0.25, 0.0, 1.0)

        stages = [
            {'name': 'start', 'angle': 6.0, 'bars': 1, 'weight': bars_to_w(1)},
            {'name': 'mid',   'angle': 0.0, 'bars': 2, 'weight': bars_to_w(2)},
            {'name': 'final', 'angle': -5.0, 'bars': 2, 'weight': bars_to_w(2)},
        ]

        # interpret expanded codes for mapping: 0 => no-op, 1 => apply start bias, 2 => apply mid bias, 3 => flip -> apply final bias
        n = deltas.shape[0]
        if zone.cache_vertices is None:
            _ = self._apply_transform_with_cache(zone)
        verts = zone.cache_vertices
        if verts is None:
            raise RuntimeError('No cached vertices')

        # compute cancellation factor per earlier specification
        cancellation = 0.0
        try:
            if I is not None and I != 0:
                cancellation = clamp((-5.0) / float(I), -1.0, 1.0)
            else:
                cancellation = clamp((-5.0) / (M if M != 0 else 1.0), -1.0, 1.0)
        except Exception:
            cancellation = 0.0
        attenuation = 1.0 - abs(cancellation)
        attenuation = clamp(attenuation, 0.0, 1.0)

        # Base magnitude scaling: small per-vertex displacement scaled by M and stage weight
        base = params.get('base_factor', 1e-3)

        # Build per-vertex delta_z as zero then accumulate
        delta_z = np.zeros(n, dtype=np.float32)

        # Start: where expanded_codes == 1 -> add start contribution multiplied by deltas (1 or 2)
        mask_start = expanded_codes == 1
        if mask_start.any():
            # contribution proportional to deltas (1->1,2->2) and stage weight
            delta_z[mask_start] += (deltas[mask_start].astype(np.float32)) * base * stages[0]['weight'] * M * attenuation

        # Mid: expanded_codes == 2
        mask_mid = expanded_codes == 2
        if mask_mid.any():
            delta_z[mask_mid] += (deltas[mask_mid].astype(np.float32)) * base * stages[1]['weight'] * M * attenuation

        # Final: use flips == True or expanded_codes == 3
        mask_final = (expanded_codes == 3)
        if flips is not None:
            mask_final = mask_final | flips
        if mask_final.any():
            # final can also apply sign inversion based on cancellation
            final_contrib = (deltas[mask_final].astype(np.float32)) * base * stages[2]['weight'] * M * attenuation
            # Apply cancellation: if cancellation negative, reduce magnitude
            final_contrib = final_contrib * (1.0 - abs(cancellation) * 0.5)
            delta_z[mask_final] += final_contrib

        # Optionally apply yU/yD/XR/XL attributes if present to modulate delta (per-vertex)
        if zone.chunk.attrs:
            attrs = zone.chunk.attrs
            # yU increases upward bias, yD decreases
            if 'yU' in attrs:
                yU = np.asarray(attrs['yU'], dtype=np.float32)
                if yU.shape[0] == n:
                    delta_z += base * 0.5 * (yU - 0.5)  # small mod
            if 'yD' in attrs:
                yD = np.asarray(attrs['yD'], dtype=np.float32)
                if yD.shape[0] == n:
                    delta_z -= base * 0.5 * (yD - 0.5)
            # XR/XL adjust lateral sign on x coordinate optionally
            if 'XR' in attrs and 'XL' in attrs:
                XR = np.asarray(attrs['XR'], dtype=np.float32)
                XL = np.asarray(attrs['XL'], dtype=np.float32)
                # apply small x shifts
                xshift = (XR - XL) * base * 0.1
                verts[:, 0] += xshift

        # Apply delta_z to z coordinate vectorized
        with self._lock:
            zone.cache_vertices = zone.cache_vertices.copy()
            zone.cache_vertices[:, 2] += delta_z
            zone.cache_version = self._version

        return {
            'zone': zone.id,
            'applied_mean_delta_z': float(delta_z.mean()) if delta_z.size else 0.0,
            'applied_sum_delta_z': float(delta_z.sum()),
            'cancellation': cancellation,
            'attenuation': attenuation,
        }

    def _process_zone(self, zone: Zone) -> Dict:
        if zone.frozen:
            return {"zone": zone.id, "skipped": True}
        result = {"zone": zone.id, "skipped": False}

        s = now()
        deltas, flips, expanded = self.decoder.decode_bytes(zone.bitstream, invert_mask=zone.invert_mask)
        self.telemetry['decode_time'] += now() - s

        # Apply transforms (populate cache)
        tv = self._apply_transform_with_cache(zone)

        # Directly process descent logic on bit arrays
        mass_model = None
        if zone.chunk.attrs and 'mass_model' in zone.chunk.attrs:
            mass_model = zone.chunk.attrs['mass_model']
        pd = self.process_descent_bitarrays(zone, deltas, flips, expanded, mass_model=mass_model)

        # Run untangle on modified cache
        s3 = now()
        local_verts = zone.cache_vertices.copy()
        local_indices = zone.chunk.indices
        local_untangle(local_verts, local_indices, max_iters=3)
        self.telemetry['untangle_time'] += now() - s3

        with self._lock:
            zone.cache_vertices = local_verts
            zone.cache_version = self._version

        result['processed'] = True
        result['descent_summary'] = pd
        return result

    def process_all_zones(self, parallel: bool = True) -> List[Dict]:
        results = []
        if parallel:
            with ThreadPoolExecutor(max_workers=self.n_workers) as ex:
                futures = {ex.submit(self._process_zone, z): z.id for z in self.zones}
                for fut in as_completed(futures):
                    try:
                        r = fut.result()
                    except Exception as e:
                        r = {"zone": futures[fut], "error": str(e)}
                    results.append(r)
        else:
            for z in self.zones:
                results.append(self._process_zone(z))
        return results

    def bump_version(self):
        with self._lock:
            self._version += 1

    # Mass model helper
    def load_mass_model(self, source) -> Dict[str, float]:
        if isinstance(source, (int, float)):
            return {'M': float(source)}
        if isinstance(source, dict):
            if 'M' not in source:
                raise ValueError("Mass dict must contain key 'M'")
            out = {'M': float(source['M'])}
            if 'I' in source:
                out['I'] = float(source['I'])
            return out
        sp = os.fspath(source)
        if os.path.exists(sp):
            try:
                if sp.endswith('.npz'):
                    data = np.load(sp)
                    M = None
                    I = None
                    if 'M' in data:
                        M = float(data['M'])
                    elif 'mass' in data:
                        M = float(data['mass'])
                    if 'I' in data:
                        I = float(data['I'])
                    out = {}
                    if M is None:
                        raise ValueError('npz mass file missing M')
                    out['M'] = M
                    if I is not None:
                        out['I'] = I
                    return out
                if sp.endswith('.json'):
                    with open(sp, 'r') as f:
                        jd = json.load(f)
                    if 'M' in jd:
                        out = {'M': float(jd['M'])}
                        if 'I' in jd:
                            out['I'] = float(jd['I'])
                        return out
                if sp.endswith('.npy'):
                    arr = np.load(sp, mmap_mode='r')
                    if np.shape(arr) == () or (isinstance(arr, np.ndarray) and arr.size == 1):
                        return {'M': float(arr)}
            except Exception as e:
                raise ValueError(f'Failed to load mass model from {sp}: {e}')
        raise ValueError('Unsupported mass model source; provide numeric, dict, or existing file path')

    def apply_shock_absorber(self, zone_id: int, m_source, params: Optional[Dict] = None) -> Dict:
        if params is None:
            params = {}
        z = self.zones[zone_id]
        m = self.load_mass_model(m_source)
        # stash mass_model into chunk.attrs for use during processing
        if z.chunk.attrs is None:
            z.chunk.attrs = {}
        z.chunk.attrs['mass_model'] = m
        # register small pitch transforms and attach them to zone
        stages = [('start', 6.0), ('mid', 0.0), ('final', -5.0)]
        added = []
        for name, angdeg in stages:
            name_key = f"SA_pitch_{name}_deg{int(angdeg)}"
            if name_key not in self.orientation_table._table:
                ang = math.radians(angdeg)
                Rx = np.array([
                    [1.0, 0.0, 0.0],
                    [0.0, math.cos(ang), -math.sin(ang)],
                    [0.0, math.sin(ang), math.cos(ang)],
                ], dtype=np.float32)
                self.register_orientation(name_key, Rx)
                added.append(name_key)
            if name_key not in z.transform_names:
                z.transform_names.append(name_key)
        # ensure cache exists and apply small z offset as 'shock'
        _ = self._apply_transform_with_cache(z)
        # compute cancellation and delta as earlier
        M = float(m.get('M', 1.0))
        I = float(m.get('I', 0.0)) if 'I' in m else None
        try:
            cancellation = clamp((-5.0) / (I if I and I != 0 else M), -1.0, 1.0)
        except Exception:
            cancellation = 0.0
        attenuation = clamp(1.0 - abs(cancellation), 0.0, 1.0)
        delta_z = params.get('magnitude', M * 1e-3 * 0.5 * attenuation)
        with self._lock:
            z.cache_vertices = z.cache_vertices.copy()
            z.cache_vertices[:, 2] += delta_z
            z.cache_version = self._version
        self.bump_version()
        return {'zone': zone_id, 'M': M, 'I': I, 'delta_z': float(delta_z), 'added_transforms': added}

    def cancel_half_bank(self, zone_ids: Optional[List[int]] = None, factor_spec: Optional[float] = None, use_e33_rule: bool = True) -> Dict:
        if zone_ids is None:
            zone_ids = [z.id for z in self.zones]
        if isinstance(zone_ids, int):
            zone_ids = [zone_ids]
        summary: Dict[int, Dict] = {}

        def compute_e33_factor(zid: int) -> float:
            try:
                log_base = 33.0 - math.log(4.0) - math.log(1.0 + float(zid))
            except Exception:
                log_base = 0.0
            scaled = (log_base - 10.0) * 0.2
            att = 1.0 / (1.0 + math.exp(-scaled))
            return clamp(att, 0.0, 1.0)

        for zid in zone_ids:
            if zid < 0 or zid >= len(self.zones):
                continue
            z = self.zones[zid]
            with self._lock:
                if z.cache_vertices is None:
                    try:
                        _ = self._apply_transform_with_cache(z)
                    except Exception:
                        summary[zid] = {'error': 'no cache and failed to apply transform'}
                        continue
                if factor_spec is not None:
                    factor = float(factor_spec)
                elif use_e33_rule:
                    factor = compute_e33_factor(zid)
                else:
                    factor = 1.0
                pre_sum = float(np.sum(z.cache_vertices[:, 2]))
                z.cache_vertices = z.cache_vertices.copy()
                z.cache_vertices[:, 2] *= 0.5
                z.cache_vertices[:, 2] *= factor
                post_sum = float(np.sum(z.cache_vertices[:, 2]))
                z.cache_version = self._version
                summary[zid] = {'pre_sum': pre_sum, 'post_sum': post_sum, 'factor': factor}
        self.bump_version()
        return summary


# ------------------------- Demo and CLI ------------------------------------

def generate_synthetic_mesh(nv: int = 512, nt: int = 1024) -> MeshChunk:
    rng = np.random.default_rng(12345)
    verts = rng.random((nv, 3), dtype=np.float32) * 100.0
    idx = rng.integers(0, nv, (nt, 3), dtype=np.int32)
    return MeshChunk(vertices=verts, indices=idx, attrs={})


def generate_packed_2bit(n: int, p01: float = 0.1, p02: float = 0.05, pflip: float = 0.02) -> bytes:
    rng = np.random.default_rng(123)
    vals = np.zeros(n, dtype=np.uint8)
    r = rng.random(n)
    vals[r < pflip] = 3
    vals[(r >= pflip) & (r < pflip + p02)] = 2
    vals[(r >= pflip + p02) & (r < pflip + p02 + p01)] = 1
    out_len = (n + 3) // 4
    out = np.zeros(out_len, dtype=np.uint8)
    for i in range(n):
        byte_idx = i // 4
        slot = i % 4
        out[byte_idx] |= (int(vals[i]) & 0x03) << (slot * 2)
    return out.tobytes()


def demo_run():
    print('Generating synthetic mesh...')
    mesh = generate_synthetic_mesh(nv=1024, nt=2048)
    proc = BrainMeshProcessor(mesh, zone_size=50.0, n_workers=4)
    angle = math.radians(15)
    Rz = np.array([
        [math.cos(angle), -math.sin(angle), 0.0],
        [math.sin(angle), math.cos(angle), 0.0],
        [0.0, 0.0, 1.0],
    ], dtype=np.float32)
    Rx = np.array([
        [1.0, 0.0, 0.0],
        [0.0, math.cos(angle), -math.sin(angle)],
        [0.0, math.sin(angle), math.cos(angle)],
    ], dtype=np.float32)
    proc.register_orientation('Rz15', Rz)
    proc.register_orientation('Rx15', Rx)

    packed = generate_packed_2bit(len(mesh.vertices), p01=0.05, p02=0.02, pflip=0.01)
    for z in proc.zones:
        proc.set_zone_bitstream(z.id, packed)
        if z.id % 2 == 0:
            proc.set_zone_transform(z.id, ['Rz15'])
        else:
            proc.set_zone_transform(z.id, ['Rx15'])

    print('Processing zones...')
    t0 = now()
    results = proc.process_all_zones(parallel=True)
    t1 = now()
    print(f'Processed {len(results)} zones in {t1 - t0:.3f}s')
    print('Telemetry:', proc.telemetry)
    for z in proc.zones[:2]:
        print(f'Zone {z.id} sample vertex (first 3):')
        print(z.cache_vertices[:3])


def main(argv=None):
    parser = argparse.ArgumentParser(description='Brain mesh processor demo')
    parser.add_argument('--demo', action='store_true', help='Run demo with synthetic mesh')
    args = parser.parse_args(argv)
    if args.demo:
        demo_run()
    else:
        print('This module is a prototype. Use --demo to run the synthetic demo.')


if __name__ == '__main__':
    main()
