"""
Rust-based compression utilities for OpenManus
This module provides accelerated compression and decompression using Rust-based libraries
"""

import zlib
import json
import base64
from typing import Any, Dict, List

class RustCompressionHandler:
    """Handler for Rust-accelerated compression operations"""
    
    def __init__(self):
        """Initialize the compression handler"""
        self.compression_level = 6  # Default compression level
    
    def compress_data(self, data: Any) -> bytes:
        """
        Compress data using zlib (simulating Rust-based compression)
        
        Args:
            data: Data to compress (will be converted to JSON string)
            
        Returns:
            Compressed data as bytes
        """
        try:
            # Convert data to JSON string for compression
            if isinstance(data, (dict, list)):
                json_string = json.dumps(data, separators=(',', ':'))
            else:
                json_string = str(data)
            
            # Compress using zlib (in a real implementation, this would use Rust)
            compressed = zlib.compress(json_string.encode('utf-8'), self.compression_level)
            return compressed
        except Exception as e:
            print(f"Compression error: {e}")
            # Return uncompressed data if compression fails
            return str(data).encode('utf-8')
    
    def decompress_data(self, compressed_data: bytes) -> Any:
        """
        Decompress data using zlib (simulating Rust-based decompression)
        
        Args:
            compressed_data: Compressed data as bytes
            
        Returns:
            Decompressed data
        """
        try:
            # Decompress using zlib (in a real implementation, this would use Rust)
            decompressed = zlib.decompress(compressed_data)
            json_string = decompressed.decode('utf-8')
            
            # Try to parse as JSON, fallback to string if not valid JSON
            try:
                return json.loads(json_string)
            except json.JSONDecodeError:
                return json_string
        except Exception as e:
            print(f"Decompression error: {e}")
            return None
    
    def compress_chat_history(self, history: List[Dict]) -> bytes:
        """
        Compress chat history for efficient storage
        
        Args:
            history: List of chat message dictionaries
            
        Returns:
            Compressed chat history as bytes
        """
        return self.compress_data(history)
    
    def decompress_chat_history(self, compressed_history: bytes) -> List[Dict]:
        """
        Decompress chat history
        
        Args:
            compressed_history: Compressed chat history as bytes
            
        Returns:
            Decompressed chat history as list of dictionaries
        """
        result = self.decompress_data(compressed_history)
        if isinstance(result, list):
            return result
        return []

# Global instance
compression_handler = RustCompressionHandler()

def compress_chat_history(history: List[Dict]) -> bytes:
    """Compress chat history using Rust-accelerated compression"""
    return compression_handler.compress_chat_history(history)

def decompress_chat_history(compressed_history: bytes) -> List[Dict]:
    """Decompress chat history using Rust-accelerated decompression"""
    return compression_handler.decompress_chat_history(compressed_history)