from typing import Any, Dict, Optional
import json
import os

from pydantic import Field

from app.tool.base import BaseTool, ToolResult
from app.brain_mesh_processor import MeshChunk, BrainMeshProcessor, clamp


class BrainMeshTool(BaseTool):
    name: str = "brain_mesh_tool"
    description: str = "Tool to load and process brain mesh zones using descent bitarrays and shock absorber logic"
    parameters: Optional[dict] = Field(default_factory=lambda: {
        "type": "object",
        "properties": {
            "action": {"type": "string", "description": "load|process|apply_shock|cancel_half|enforce"},
            "source": {"type": "string", "description": "path to mesh dir or npz or numeric mass"},
            "zone_id": {"type": "integer"},
            "params": {"type": "object"}
        },
        "required": ["action"]
    })

    # Keep a simple in-memory store for processor instances (single)
    _processor: Optional[BrainMeshProcessor] = None
    _mesh: Optional[MeshChunk] = None

    async def execute(self, **kwargs) -> ToolResult:
        action = kwargs.get('action')
        source = kwargs.get('source')
        zone_id = kwargs.get('zone_id', 0)
        params = kwargs.get('params') or {}

        try:
            if action == 'load':
                if not source:
                    return self.fail_response('source is required for load')
                # load mesh
                mesh = MeshChunk.load_brain_core(source)
                self._mesh = mesh
                # create processor
                proc = BrainMeshProcessor(mesh)
                self._processor = proc
                return self.success_response({'status': 'loaded', 'vertices': int(mesh.vertices.shape[0]), 'indices': int(mesh.indices.shape[0])})

            if action == 'process':
                if not self._processor:
                    return self.fail_response('processor not initialized; call load first')
                # if params include a packed_bitstream, set it for all zones
                packed = params.get('packed_bitstream')
                if packed:
                    # packed should be a bytes-like base64 or raw; accept path too
                    if isinstance(packed, str) and os.path.exists(packed):
                        with open(packed, 'rb') as f:
                            data = f.read()
                    elif isinstance(packed, (bytes, bytearray)):
                        data = packed
                    else:
                        # try to parse JSON array
                        try:
                            data = bytes(params.get('packed_bitstream_bytes', []))
                        except Exception:
                            data = None
                    if data:
                        for z in self._processor.zones:
                            self._processor.set_zone_bitstream(z.id, data)
                results = self._processor.process_all_zones(parallel=True)
                return self.success_response({'status': 'processed', 'results': results})

            if action == 'apply_shock':
                if not self._processor:
                    return self.fail_response('processor not initialized; call load first')
                m_source = source or params.get('m_source', 1.0)
                res = self._processor.apply_shock_absorber(zone_id, m_source, params=params)
                return self.success_response(res)

            if action == 'cancel_half':
                if not self._processor:
                    return self.fail_response('processor not initialized; call load first')
                zone_ids = params.get('zone_ids')
                factor_spec = params.get('factor_spec')
                use_e33 = params.get('use_e33_rule', True)
                res = self._processor.cancel_half_bank(zone_ids=zone_ids, factor_spec=factor_spec, use_e33_rule=use_e33)
                return self.success_response(res)

            if action == 'enforce':
                """Compute and apply an enforcement plan derived from current mesh zones.

                Behavior:
                  - If zone_ids provided in params, enforce for those zones; otherwise all zones.
                  - Build enforcement actions: adapter scaling, per-layer multipliers, attention gains.
                  - If a local model handler is available and exposes apply_adapter_scales or set_layer_multipliers,
                    call those to apply enforcement at inference time. Otherwise return the plan for external application.
                """
                if not self._processor:
                    return self.fail_response('processor not initialized; call load first')
                zone_ids = params.get('zone_ids')
                if zone_ids is None:
                    zone_ids = [z.id for z in self._processor.zones]
                if isinstance(zone_ids, int):
                    zone_ids = [zone_ids]

                plan: Dict[int, Dict[str, Any]] = {}
                for zid in zone_ids:
                    if zid < 0 or zid >= len(self._processor.zones):
                        continue
                    z = self._processor.zones[zid]
                    if z.cache_vertices is None:
                        # attempt to populate cache
                        try:
                            _ = self._processor._apply_transform_with_cache(z)
                        except Exception:
                            plan[zid] = {'error': 'no cache available'}
                            continue
                    verts = z.cache_vertices
                    mean_z = float(verts[:, 2].mean()) if verts.size else 0.0
                    std_z = float(verts[:, 2].std()) if verts.size else 0.0
                    # compute adapter scale: inversely proportional to mean_z magnitude
                    adapter_scale = clamp(1.0 - abs(mean_z) * 0.1, 0.0, 1.0)
                    # attention gain proportional to mean_z but clamped
                    attention_gain = clamp(mean_z * 10.0, -2.0, 2.0)
                    # layer multiplier example: top layers scaled by adapter_scale
                    layer_actions = {"top_k": 4, "multiplier": adapter_scale}
                    plan[zid] = {
                        'mean_z': mean_z,
                        'std_z': std_z,
                        'adapter_scale': adapter_scale,
                        'attention_gain': attention_gain,
                        'layer_actions': layer_actions,
                    }

                # Attempt to apply enforcement to local model handler if available
                applied = {}
                try:
                    from app.config import config
                    mh = getattr(config, 'local_model_handler', None)
                    if mh is not None:
                        # apply adapter scales if available
                        if hasattr(mh, 'apply_adapter_scales'):
                            # map plan into adapter name -> scale
                            adapter_map = {f'adapter_zone_{zid}': plan[zid]['adapter_scale'] for zid in plan if 'adapter_scale' in plan[zid]}
                            mh.apply_adapter_scales(adapter_map)
                            applied['adapters'] = adapter_map
                        # apply layer multipliers if supported
                        if hasattr(mh, 'set_layer_multipliers'):
                            # generate simple layer multipliers
                            layer_map = {str(i): plan[zid]['layer_actions']['multiplier'] for zid in plan for i in range(plan[zid]['layer_actions']['top_k'])}
                            mh.set_layer_multipliers(layer_map)
                            applied['layers'] = layer_map
                        # apply attention gains if supported
                        if hasattr(mh, 'set_attention_gains'):
                            gains = {str(zid): plan[zid]['attention_gain'] for zid in plan}
                            mh.set_attention_gains(gains)
                            applied['attention'] = gains
                except Exception:
                    # do not fail if application to model handler not possible
                    applied['error'] = 'failed to call model handler methods or none present'

                return self.success_response({'status': 'enforced', 'plan': plan, 'applied': applied})

            return self.fail_response(f'Unknown action: {action}')
        except Exception as e:
            return self.fail_response(str(e))
