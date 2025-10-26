"""
Query Management System for OpenManus
This module implements a queue-based message management system with compression and reconstruction capabilities
to prevent model crashes or overload while maintaining 90% of the original structure.
"""

import asyncio
import threading
import time
import json
import hashlib
import logging
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, asdict
from collections import deque
import zlib
import re

logger = logging.getLogger(__name__)

@dataclass
class QueuedQuery:
    """Represents a queued user query with metadata"""
    id: str
    original_message: str
    compressed_message: str
    compression_ratio: float
    timestamp: float
    priority: int  # 1-10, higher is more urgent
    status: str  # pending, processing, completed, failed
    reconstructed_message: Optional[str] = None
    processing_start_time: Optional[float] = None
    processing_end_time: Optional[float] = None

class QueryCompressor:
    """Handles compression and reconstruction of user queries"""
    
    def __init__(self):
        # Common words that can be safely compressed
        self.common_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were',
            'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might',
            'can', 'must', 'shall', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
            'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their', 'myself', 'yourself',
            'himself', 'herself', 'itself', 'ourselves', 'yourselves', 'themselves'
        }
        
        # Abbreviation mappings for compression
        self.abbreviations = {
            'information': 'info',
            'application': 'app',
            'technology': 'tech',
            'communication': 'comm',
            'organization': 'org',
            'government': 'gov',
            'university': 'uni',
            'international': 'intl',
            'development': 'dev',
            'management': 'mgmt',
            'marketing': 'mkt',
            'engineering': 'eng',
            'operation': 'ops',
            'configuration': 'config',
            'implementation': 'impl',
            'specification': 'spec',
            'documentation': 'doc',
            'calculation': 'calc',
            'identification': 'id',
            'authentication': 'auth',
            'authorization': 'authz'
        }
    
    def compress_message(self, message: str) -> Tuple[str, float]:
        """
        Compress a message while maintaining 90% of original structure
        
        Args:
            message: Original user message
            
        Returns:
            Tuple of (compressed_message, compression_ratio)
        """
        if not message:
            return message, 1.0
            
        original_length = len(message)
        
        # Apply light compression techniques
        compressed = message
        
        # 1. Remove extra whitespace (preserves single spaces)
        compressed = re.sub(r'\s+', ' ', compressed).strip()
        
        # 2. Replace common words with abbreviations (only if they save space)
        for full_word, abbrev in self.abbreviations.items():
            if len(abbrev) < len(full_word):
                # Only replace if it actually saves characters
                pattern = r'\b' + re.escape(full_word) + r'\b'
                compressed = re.sub(pattern, abbrev, compressed, flags=re.IGNORECASE)
        
        # 3. Remove redundant punctuation (but preserve sentence structure)
        # This is a conservative approach to maintain 90% structure
        compressed = re.sub(r'([.!?])\1+', r'\1', compressed)  # Multiple punctuation to single
        compressed = re.sub(r'([,;:])\1+', r'\1', compressed)  # Multiple commas/semicolons to single
        
        # Calculate compression ratio
        compressed_length = len(compressed)
        compression_ratio = compressed_length / original_length if original_length > 0 else 1.0
        
        logger.debug(f"Message compression: {original_length} -> {compressed_length} chars ({compression_ratio:.2%})")
        
        return compressed, compression_ratio
    
    def reconstruct_message(self, compressed_message: str, original_message: str) -> str:
        """
        Reconstruct the original message from compressed version
        
        Args:
            compressed_message: Compressed message
            original_message: Original message for reference
            
        Returns:
            Reconstructed message with 100% accuracy
        """
        # For this implementation, we'll use the original message as the reconstructed version
        # In a more advanced system, we could store a mapping of changes and reverse them
        return original_message

class QueryQueue:
    """Manages the queue of incoming queries with priority and rate limiting"""
    
    def __init__(self, max_queue_size: int = 100, max_concurrent_processing: int = 3):
        self.max_queue_size = max_queue_size
        self.max_concurrent_processing = max_concurrent_processing
        self.queue = deque()
        self.processing = set()
        self.completed = {}
        self.lock = threading.RLock()
        self.compressor = QueryCompressor()
        self.stats = {
            'total_queued': 0,
            'total_processed': 0,
            'total_failed': 0,
            'avg_queue_time': 0.0,
            'avg_processing_time': 0.0
        }
        # Track processing timeouts
        self.processing_timeouts = {}
    
    def enqueue_query(self, message: str, priority: int = 5) -> str:
        """
        Add a query to the queue
        
        Args:
            message: User query message
            priority: Priority level (1-10)
            
        Returns:
            Query ID
        """
        with self.lock:
            # Check queue size limit
            if len(self.queue) >= self.max_queue_size:
                raise Exception("Query queue is full. Please try again later.")
            
            # Generate unique ID
            query_id = hashlib.md5(f"{message}{time.time()}".encode()).hexdigest()[:16]
            
            # Compress message
            compressed_message, compression_ratio = self.compressor.compress_message(message)
            
            # Create queued query
            queued_query = QueuedQuery(
                id=query_id,
                original_message=message,
                compressed_message=compressed_message,
                compression_ratio=compression_ratio,
                timestamp=time.time(),
                priority=priority,
                status='pending'
            )
            
            # Add to queue (higher priority items go to the front)
            inserted = False
            for i, existing_query in enumerate(self.queue):
                if existing_query.priority < priority:
                    self.queue.insert(i, queued_query)
                    inserted = True
                    break
            
            if not inserted:
                self.queue.append(queued_query)
            
            self.stats['total_queued'] += 1
            logger.info(f"Query {query_id} enqueued with priority {priority}")
            
            return query_id
    
    def get_next_query(self) -> Optional[QueuedQuery]:
        """
        Get the next query to process (highest priority first)
        
        Returns:
            Next query to process or None if queue is empty
        """
        with self.lock:
            if not self.queue:
                return None
            
            # Get highest priority query
            query = self.queue.popleft()
            query.status = 'processing'
            query.processing_start_time = time.time()
            self.processing.add(query.id)
            # Set timeout for processing (increased to 10 minutes for large model loading)
            self.processing_timeouts[query.id] = time.time() + 600  # 10 minutes instead of 5
            
            logger.info(f"Query {query.id} started processing with 10-minute timeout")
            return query
    
    def complete_query(self, query_id: str, result: Any) -> None:
        """
        Mark a query as completed
        
        Args:
            query_id: Query ID
            result: Processing result
        """
        with self.lock:
            # Find query in processing set
            if query_id in self.processing:
                self.processing.remove(query_id)
                # Remove timeout tracking
                if query_id in self.processing_timeouts:
                    del self.processing_timeouts[query_id]
                
                # Update stats
                self.stats['total_processed'] += 1
                
                logger.info(f"Query {query_id} completed successfully")
    
    def fail_query(self, query_id: str, error: str) -> None:
        """
        Mark a query as failed
        
        Args:
            query_id: Query ID
            error: Error message
        """
        with self.lock:
            # Find query in processing set
            if query_id in self.processing:
                self.processing.remove(query_id)
                # Remove timeout tracking
                if query_id in self.processing_timeouts:
                    del self.processing_timeouts[query_id]
                
                # Update stats
                self.stats['total_failed'] += 1
                
                logger.error(f"Query {query_id} failed: {error}")
    
    def check_timeouts(self) -> List[str]:
        """
        Check for timed out queries and return their IDs
        
        Returns:
            List of timed out query IDs
        """
        timed_out_queries = []
        current_time = time.time()
        
        with self.lock:
            # Check for timed out queries
            timed_out_ids = [
                query_id for query_id, timeout in self.processing_timeouts.items()
                if current_time > timeout
            ]
            
            # Mark timed out queries as failed
            for query_id in timed_out_ids:
                if query_id in self.processing:
                    self.processing.remove(query_id)
                    if query_id in self.processing_timeouts:
                        del self.processing_timeouts[query_id]
                    self.stats['total_failed'] += 1
                    timed_out_queries.append(query_id)
                    logger.error(f"Query {query_id} timed out after 10 minutes")
        
        return timed_out_queries
    
    def reconstruct_query_message(self, query: QueuedQuery) -> str:
        """
        Reconstruct the original message for processing
        
        Args:
            query: Queued query
            
        Returns:
            Reconstructed message
        """
        reconstructed = self.compressor.reconstruct_message(
            query.compressed_message, 
            query.original_message
        )
        query.reconstructed_message = reconstructed
        return reconstructed
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics"""
        with self.lock:
            return {
                'queue_size': len(self.queue),
                'processing_count': len(self.processing),
                'stats': self.stats.copy()
            }




class QueryManager:
    """Main query management system"""
    
    def __init__(self, max_queue_size: int = 100, max_concurrent_processing: int = 3):
        self.queue = QueryQueue(max_queue_size, max_concurrent_processing)
        self.is_running = False
        self.worker_thread = None
        self.processing_callback = None
        self.async_processing_callback = None
        self.results = {}  # Store results for async retrieval
        self.results_lock = threading.Lock()
        self.timeout_checker_thread = None  # Add timeout checker thread
        
    def set_processing_callback(self, callback):
        """
        Set the callback function for processing queries
        
        Args:
            callback: Function to call for processing queries
        """
        self.processing_callback = callback
    
    def set_async_processing_callback(self, callback):
        """
        Set the async callback function for processing queries
        
        Args:
            callback: Async function to call for processing queries
        """
        self.async_processing_callback = callback
    
    def enqueue_user_query(self, message: str, priority: int = 5) -> str:
        """
        Enqueue a user query
        
        Args:
            message: User message
            priority: Priority level (1-10)
            
        Returns:
            Query ID
        """
        return self.queue.enqueue_query(message, priority)
    
    def get_query_result(self, query_id: str) -> Optional[Any]:
        """
        Get the result of a processed query
        
        Args:
            query_id: Query ID
            
        Returns:
            Query result or None if not available
        """
        with self.results_lock:
            return self.results.get(query_id)
    
    def store_query_result(self, query_id: str, result: Any):
        """
        Store the result of a processed query
        
        Args:
            query_id: Query ID
            result: Query result
        """
        with self.results_lock:
            self.results[query_id] = result
    
    def start_processing(self):
        """Start the query processing worker"""
        if not self.is_running:
            self.is_running = True
            self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
            self.worker_thread.start()
            
            # Start timeout checker thread
            self.timeout_checker_thread = threading.Thread(target=self._timeout_checker_loop, daemon=True)
            self.timeout_checker_thread.start()
            
            logger.info("Query manager processing started")
    
    def stop_processing(self):
        """Stop the query processing worker"""
        self.is_running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=5)
        if self.timeout_checker_thread:
            self.timeout_checker_thread.join(timeout=5)
        logger.info("Query manager processing stopped")
    
    def _timeout_checker_loop(self):
        """Loop to check for timed out queries"""
        while self.is_running:
            try:
                # Check for timed out queries every 10 seconds (reduced from 30)
                timed_out_queries = self.queue.check_timeouts()
                for query_id in timed_out_queries:
                    # Store timeout error result
                    self.store_query_result(query_id, {
                        "error": "Query processing timed out after 10 minutes"
                    })
                    logger.info(f"⏰ Query {query_id} marked as timed out")
                time.sleep(10)  # Check more frequently for better responsiveness
            except Exception as e:
                logger.error(f"Error in timeout checker loop: {e}")
                time.sleep(10)

    def _worker_loop(self):
        """Worker loop for processing queued queries"""
        # Create a new event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        while self.is_running:
            try:
                # Get next query to process
                query = self.queue.get_next_query()
                
                if query and (self.processing_callback or self.async_processing_callback):
                    try:
                        # Reconstruct original message
                        reconstructed_message = self.queue.reconstruct_query_message(query)
                        
                        # Process the query
                        if self.async_processing_callback:
                            # For async processing, we need to run in an event loop
                            result = loop.run_until_complete(
                                self.async_processing_callback(reconstructed_message, query)
                            )
                        elif self.processing_callback:
                            result = self.processing_callback(reconstructed_message, query)
                        else:
                            result = "No processing callback available"
                        
                        # If result is a coroutine, resolve it
                        if asyncio.iscoroutine(result):
                            result = loop.run_until_complete(result)
                        
                        # Store result and mark as completed
                        self.store_query_result(query.id, result)
                        self.queue.complete_query(query.id, result)
                        logger.info(f"✅ Query {query.id} completed successfully")
                        
                    except Exception as e:
                        logger.error(f"Error processing query {query.id}: {e}")
                        import traceback
                        logger.error(f"Traceback: {traceback.format_exc()}")
                        self.queue.fail_query(query.id, str(e))
                        # Store error result
                        self.store_query_result(query.id, {
                            "error": str(e)
                        })
                else:
                    # No queries to process, sleep briefly
                    time.sleep(0.1)
                    
            except Exception as e:
                logger.error(f"Error in query worker loop: {e}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                time.sleep(1)
        
        # Clean up the event loop
        loop.close()
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        return self.queue.get_queue_stats()

# Global instance
query_manager = QueryManager()

def enqueue_query(message: str, priority: int = 5) -> str:
    """
    Enqueue a user query
    
    Args:
        message: User message
        priority: Priority level (1-10)
        
    Returns:
        Query ID
    """
    return query_manager.enqueue_user_query(message, priority)

def get_query_result(query_id: str) -> Optional[Any]:
    """
    Get the result of a processed query
    
    Args:
        query_id: Query ID
        
    Returns:
        Query result or None if not available
    """
    return query_manager.get_query_result(query_id)

def start_query_processing():
    """Start query processing"""
    query_manager.start_processing()

def stop_query_processing():
    """Stop query processing"""
    query_manager.stop_processing()

def set_query_processor(callback):
    """
    Set the query processing callback
    
    Args:
        callback: Function to process queries
    """
    query_manager.set_processing_callback(callback)

def set_async_query_processor(callback):
    """
    Set the async query processing callback
    
    Args:
        callback: Async function to process queries
    """
    query_manager.set_async_processing_callback(callback)

def get_query_stats() -> Dict[str, Any]:
    """Get query system statistics"""
    return query_manager.get_system_stats()
