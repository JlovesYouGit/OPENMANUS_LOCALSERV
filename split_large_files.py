#!/usr/bin/env python3
"""
Simple script to split large model files into smaller chunks for GitHub.
"""

import os
import shutil
from pathlib import Path

def split_file(file_path, chunk_size_mb=50):
    """Split a large file into smaller chunks."""
    chunk_size = chunk_size_mb * 1024 * 1024  # Convert MB to bytes
    file_size = os.path.getsize(file_path)
    
    print(f"Splitting {file_path} ({file_size / (1024*1024):.1f} MB) into {chunk_size_mb}MB chunks...")
    
    if file_size <= chunk_size:
        print("File is already smaller than chunk size, no splitting needed.")
        return []
    
    chunks = []
    with open(file_path, 'rb') as f:
        chunk_num = 0
        while True:
            chunk_data = f.read(chunk_size)
            if not chunk_data:
                break
                
            chunk_path = f"{file_path}.part{chunk_num:04d}"
            with open(chunk_path, 'wb') as chunk_file:
                chunk_file.write(chunk_data)
            
            chunks.append(chunk_path)
            print(f"Created chunk: {os.path.basename(chunk_path)} ({len(chunk_data) / (1024*1024):.1f} MB)")
            chunk_num += 1
    
    print(f"Split into {len(chunks)} chunks")
    return chunks

def create_readme_for_split_files(split_files_dir):
    """Create a README file with instructions for reassembling split files."""
    readme_content = """# Split Model Files

This directory contains large model files that have been split into smaller chunks for GitHub storage.

## Reassembling Files

To reassemble the split files, use the following commands on Linux/macOS:

```bash
# Example for a file split into 3 parts
cat model.safetensors.part0000 model.safetensors.part0001 model.safetensors.part0002 > model.safetensors
```

On Windows, use:

```cmd
copy /b model.safetensors.part0000 + model.safetensors.part0001 + model.safetensors.part0002 model.safetensors
```

## File List

"""
    
    # Add list of split files
    split_files = list(Path(split_files_dir).glob("*.part*"))
    if split_files:
        readme_content += "The following files have been split:\n\n"
        for file in split_files:
            readme_content += f"- {file.name}\n"
    
    readme_content += """
## Important Notes

1. Always reassemble chunks in numerical order (part0000, part0001, part0002, etc.)
2. Verify file integrity after reassembly if possible
3. Some chunks may be smaller than 50MB (typically the last chunk)
"""
    
    readme_path = os.path.join(split_files_dir, "README_SPLIT_FILES.md")
    with open(readme_path, 'w') as f:
        f.write(readme_content)
    
    print(f"README created at {readme_path}")

def main():
    """Main function to split large model files."""
    # Define the large model files to split
    large_files = [
        "models/phi-3-mini/model-00001-of-00002.safetensors",
        "models/phi-3-mini/model-00002-of-00002.safetensors",
        "models/qwen2-0.5b/model.safetensors",
    ]
    
    print("Splitting large model files...")
    
    split_count = 0
    for file_path in large_files:
        if os.path.exists(file_path):
            print(f"\nProcessing {file_path}")
            chunks = split_file(file_path, chunk_size_mb=50)
            if chunks:
                split_count += len(chunks)
        else:
            print(f"File not found: {file_path}")
    
    print(f"\n✅ Splitting completed. Created {split_count} chunks.")
    
    # Create README
    create_readme_for_split_files("models/phi-3-mini")
    create_readme_for_split_files("models/qwen2-0.5b")

if __name__ == "__main__":
    main()