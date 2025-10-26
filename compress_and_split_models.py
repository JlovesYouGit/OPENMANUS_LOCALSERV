#!/usr/bin/env python3
"""
Script to compress and split large model files into smaller chunks for GitHub compatibility.
"""

import os
import sys
import shutil
from pathlib import Path

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

def get_large_files(directory, min_size_mb=100):
    """Get all files in directory larger than min_size_mb."""
    large_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                # Skip .part files as they are already split chunks
                if file.endswith('.part'):
                    continue
                size_mb = os.path.getsize(file_path) / (1024 * 1024)
                if size_mb > min_size_mb:
                    large_files.append((file_path, size_mb))
            except OSError:
                pass
    return large_files

def main():
    # Define the source directory for models
    source_models_dir = "N:\\Openmanus\\OpenManus\\models"
    
    # Check if source directory exists
    if not os.path.exists(source_models_dir):
        print(f"Source models directory not found: {source_models_dir}")
        return 1
    
    # Get large files
    large_files = get_large_files(source_models_dir, 50)  # Files larger than 50MB
    
    print(f"Found {len(large_files)} large files to process:")
    for file_path, size_mb in large_files:
        print(f"  {file_path} ({size_mb:.1f} MB)")
    
    # Create models directory in Lite repo if it doesn't exist
    lite_models_dir = "models"
    if not os.path.exists(lite_models_dir):
        os.makedirs(lite_models_dir)
    
    # Process each large file one at a time
    for i, (file_path, size_mb) in enumerate(large_files):
        print(f"\n[{i+1}/{len(large_files)}] Processing: {file_path}")
        
        # Get relative path from source models directory
        relative_path = os.path.relpath(file_path, source_models_dir)
        dest_path = os.path.join(lite_models_dir, relative_path)
        
        # Create destination directory if needed
        dest_dir = os.path.dirname(dest_path)
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
        
        # Copy file to Lite repo first
        print(f"Copying to: {dest_path}")
        try:
            shutil.copy2(file_path, dest_path)
            print(f"Copy completed: {dest_path}")
        except Exception as e:
            print(f"Error copying file {file_path}: {e}")
            continue
        
        # For files larger than 100MB, we'll split them
        if size_mb > 100:
            # Split the file
            if split_file(dest_path, 50):  # Split into 50MB chunks
                # Remove original file after successful splitting
                try:
                    os.remove(dest_path)
                    print(f"Removed original file: {dest_path}")
                except Exception as e:
                    print(f"Error removing original file {dest_path}: {e}")
            else:
                print(f"Failed to split file: {dest_path}")
        else:
            print(f"File is smaller than 100MB, keeping as is: {dest_path}")
    
    print("\nModel processing complete!")
    return 0

if __name__ == "__main__":
    sys.exit(main())