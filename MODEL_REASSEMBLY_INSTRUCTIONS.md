# Model File Reassembly Instructions

This document provides instructions on how to reassemble the split model files that were chunked for GitHub compatibility.

## Overview

Large model files have been split into smaller chunks (50MB each) to comply with GitHub's file size limitations. Each chunk has a `.partXXXX` extension where XXXX is a zero-padded number (e.g., `.part0000`, `.part0001`, etc.).

## Reassembly Instructions

### For Linux/macOS:

```bash
# Navigate to the directory containing the split files
cd models/

# Reassemble a split file (example with tinyllama model)
cat tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf.part* > tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf

# Verify the reassembled file
ls -la tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf
```

### For Windows:

```cmd
# Navigate to the directory containing the split files
cd models\

# Reassemble a split file (example with tinyllama model)
copy /b tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf.part* tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf

# Verify the reassembled file
dir tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf
```

## Split Files List

The following model files have been split into chunks:

1. `tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf` - Split into 13 chunks (0000-0012)
2. `phi-3-mini\model-00001-of-00002.safetensors` - Split into multiple chunks
3. `phi-3-mini\model-00002-of-00002.safetensors` - Split into multiple chunks
4. `tinyllama\model.safetensors` - Split into multiple chunks
5. `tinyllama-test\model.safetensors` - Split into multiple chunks
6. `qwen2-0.5b\model.safetensors` - Split into multiple chunks
7. `models--microsoft--Phi-3-mini-4k-instruct\blobs\*.incomplete` - Split into multiple chunks
8. `models--TinyLlama--TinyLlama-1.1B-Chat-v1.0\blobs\*.incomplete` - Split into multiple chunks

## Verification

After reassembling the files, you can verify the integrity by checking the file size matches the original or by using checksum verification if provided.

## Important Notes

1. Make sure to reassemble all chunks in the correct order
2. Do not rename the chunk files before reassembling
3. Ensure you have sufficient disk space for both the chunks and the reassembled file
4. The reassembled file should have the same name as the original file (without the .partXXXX extensions)