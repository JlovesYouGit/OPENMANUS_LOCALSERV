# Model File Splitting Instructions

To make the large model files suitable for GitHub storage, we've split them into smaller 50MB chunks.

## Split Files

The following large model files have been split:

1. `models/phi-3-mini/model-00001-of-00002.safetensors` - Split into 95 chunks
2. `models/phi-3-mini/model-00002-of-00002.safetensors` - Split into 51 chunks
3. `models/qwen2-0.5b/model.safetensors` - Split into 19 chunks

## Reassembling Files

To reassemble the original files, use the following commands:

### On Linux/macOS:
```bash
# Phi-3 Mini model part 1
cat models/phi-3-mini/model-00001-of-00002.safetensors.part* > models/phi-3-mini/model-00001-of-00002.safetensors

# Phi-3 Mini model part 2
cat models/phi-3-mini/model-00002-of-00002.safetensors.part* > models/phi-3-mini/model-00002-of-00002.safetensors

# Qwen2 0.5B model
cat models/qwen2-0.5b/model.safetensors.part* > models/qwen2-0.5b/model.safetensors
```

### On Windows:
```cmd
# Phi-3 Mini model part 1
copy /b models\phi-3-mini\model-00001-of-00002.safetensors.part* models\phi-3-mini\model-00001-of-00002.safetensors

# Phi-3 Mini model part 2
copy /b models\phi-3-mini\model-00002-of-00002.safetensors.part* models\phi-3-mini\model-00002-of-00002.safetensors

# Qwen2 0.5B model
copy /b models\qwen2-0.5b\model.safetensors.part* models\qwen2-0.5b\model.safetensors
```

## Important Notes

1. **Order Matters**: Always reassemble chunks in alphabetical order (part0000, part0001, part0002, etc.)

2. **Verification**: After reassembly, verify the file integrity by comparing file sizes or checksums with the original files if available.

3. **Storage**: The split files take up more space than the original due to filesystem overhead, but they can be stored and transferred more easily.

4. **Cleanup**: After reassembling, you can delete the .part* files to save space.

5. **Performance**: Splitting and reassembling large files can take significant time depending on your storage speed.

## File Sizes

| Original File | Size | Number of Chunks |
|---------------|------|------------------|
| models/phi-3-mini/model-00001-of-00002.safetensors | ~4.7 GB | 95 chunks |
| models/phi-3-mini/model-00002-of-00002.safetensors | ~2.5 GB | 51 chunks |
| models/qwen2-0.5b/model.safetensors | ~942 MB | 19 chunks |

## GitHub Storage

With the files split into 50MB chunks, they can now be pushed to GitHub without hitting the file size limits. Each chunk is well below GitHub's 100MB file size limit and LFS's 2GB file size limit.