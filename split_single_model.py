#!/usr/bin/env python3
"""
Script to split a single large model file into smaller chunks.
"""

import os
import sys
import shutil

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
    
    # Remove any existing chunk files
    base_path = file_path
    chunk_files = []
    for item in os.listdir(os.path.dirname(base_path)):
        if item.startswith(os.path.basename(base_path) + ".part"):
            chunk_file = os.path.join(os.path.dirname(base_path), item)
            chunk_files.append(chunk_file)
    
    # Delete existing chunk files
    for chunk_file in chunk_files:
        try:
            os.remove(chunk_file)
            print(f"Removed existing chunk: {chunk_file}")
        except OSError as e:
            print(f"Error removing existing chunk {chunk_file}: {e}")
    
    chunks = []
    with open(file_path, 'rb') as f:
        chunk_num = 0
        while True:
            chunk_data = f.read(chunk_size)
            if not chunk_data:
                break
                
            chunk_path = f"{base_path}.part{chunk_num:04d}"
            with open(chunk_path, 'wb') as chunk_file:
                chunk_file.write(chunk_data)
            
            chunks.append(chunk_path)
            chunk_size_actual = len(chunk_data) / (1024*1024)
            print(f"Created chunk {chunk_num:04d}: {os.path.basename(chunk_path)} ({chunk_size_actual:.1f} MB)")
            chunk_num += 1
    
    print(f"Split into {len(chunks)} chunks")
    return True

def main():
    if len(sys.argv) < 2:
        print("Usage: python split_single_model.py <file_path>")
        return 1
    
    file_path = sys.argv[1]
    
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return 1
    
    # Get file size
    file_size = os.path.getsize(file_path)
    size_mb = file_size / (1024 * 1024)
    
    print(f"Processing file: {file_path}")
    print(f"File size: {size_mb:.1f} MB")
    
    # For files larger than 100MB, split them
    if size_mb > 100:
        if split_file(file_path, 50):  # Split into 50MB chunks
            print("File splitting completed successfully!")
        else:
            print("File splitting failed!")
            return 1
    else:
        print("File is smaller than 100MB, no splitting needed.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())