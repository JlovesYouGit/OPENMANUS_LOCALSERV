#!/usr/bin/env python3
"""
Script to split a single large file into smaller chunks.
"""

import os
import sys

def split_file(file_path, chunk_size_mb=50):
    """Split a large file into smaller chunks."""
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found")
        return False
    
    chunk_size = chunk_size_mb * 1024 * 1024  # Convert MB to bytes
    file_size = os.path.getsize(file_path)
    
    print(f"Splitting {file_path}")
    print(f"File size: {file_size / (1024*1024):.1f} MB")
    print(f"Chunk size: {chunk_size_mb} MB")
    
    if file_size <= chunk_size:
        print("File is already smaller than chunk size, no splitting needed.")
        return True
    
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
            chunk_size_mb = len(chunk_data) / (1024*1024)
            print(f"Created chunk {chunk_num:04d}: {os.path.basename(chunk_path)} ({chunk_size_mb:.1f} MB)")
            chunk_num += 1
    
    print(f"Split into {len(chunks)} chunks")
    return True

def main():
    """Main function to split a single file."""
    if len(sys.argv) < 2:
        print("Usage: python split_single_file.py <file_path> [chunk_size_mb]")
        print("Example: python split_single_file.py models/phi-3-mini/model-00001-of-00002.safetensors 50")
        return
    
    file_path = sys.argv[1]
    chunk_size_mb = 50
    
    if len(sys.argv) > 2:
        try:
            chunk_size_mb = int(sys.argv[2])
        except ValueError:
            print("Invalid chunk size, using default 50 MB")
    
    success = split_file(file_path, chunk_size_mb)
    
    if success:
        print(f"\n✅ Splitting completed for {file_path}")
    else:
        print(f"\n❌ Splitting failed for {file_path}")

if __name__ == "__main__":
    main()