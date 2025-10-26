"""
Advanced Chat History Management with Graph-Based Compression
This module implements a Node.js module-based approach for storing conversation data
with intelligent compression through graph-style node-based compression system.
"""

import json
import os
import hashlib
import zlib
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict, field
from collections import defaultdict

@dataclass
class ChatNode:
    """Represents a node in the chat history graph"""
    id: str
    content: str
    role: str  # 'user' or 'assistant'
    timestamp: str
    connections: List[str]  # IDs of connected nodes
    importance_score: float = 0.0
    keywords: List[str] = field(default_factory=list)
    embedding: List[float] = field(default_factory=list)

class GraphBasedChatHistory:
    """Graph-based chat history manager with intelligent compression"""
    
    def __init__(self, storage_path: str = "chat_history_graph.bin"):
        self.storage_path = storage_path
        self.nodes: Dict[str, ChatNode] = {}
        self.session_id: str = self._generate_session_id()
        self.conversation_graph: Dict[str, List[str]] = defaultdict(list)
        self.max_nodes = 100  # Maximum number of nodes to keep in memory
    
    def _generate_session_id(self) -> str:
        """Generate a unique session ID"""
        return hashlib.md5(str(datetime.now().timestamp()).encode()).hexdigest()[:8]
    
    def _generate_node_id(self, content: str, role: str) -> str:
        """Generate a unique node ID based on content and role"""
        return hashlib.md5(f"{content}_{role}_{datetime.now().timestamp()}".encode()).hexdigest()[:12]
    
    def _extract_keywords(self, content: str) -> List[str]:
        """Extract important keywords from content"""
        # Simple keyword extraction (in a real implementation, this would use NLP)
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'}
        words = [word.lower().strip('.,!?;:"') for word in content.split()]
        return [word for word in words if word not in stop_words and len(word) > 2]
    
    def _calculate_importance(self, content: str, role: str) -> float:
        """Calculate importance score for a message"""
        # Simple importance calculation based on length and keywords
        keywords = self._extract_keywords(content)
        base_score = len(content) / 100.0
        keyword_score = len(keywords) / 10.0
        role_multiplier = 1.2 if role == 'user' else 1.0  # User messages slightly more important
        return (base_score + keyword_score) * role_multiplier
    
    def add_message(self, content: str, role: str, connections: Optional[List[str]] = None) -> str:
        """Add a message to the chat history graph"""
        node_id = self._generate_node_id(content, role)
        keywords = self._extract_keywords(content)
        importance_score = self._calculate_importance(content, role)
        
        node = ChatNode(
            id=node_id,
            content=content,
            role=role,
            timestamp=datetime.now().isoformat(),
            connections=connections or [],
            importance_score=importance_score,
            keywords=keywords
        )
        
        self.nodes[node_id] = node
        
        # Add to conversation graph
        if connections:
            for conn_id in connections:
                self.conversation_graph[conn_id].append(node_id)
                self.conversation_graph[node_id].append(conn_id)
        elif self.nodes:
            # Connect to the most recent node
            last_node_id = list(self.nodes.keys())[-2] if len(self.nodes) > 1 else None
            if last_node_id:
                self.conversation_graph[last_node_id].append(node_id)
                self.conversation_graph[node_id].append(last_node_id)
                node.connections.append(last_node_id)
        
        # Manage memory by pruning old nodes if we exceed the limit
        self._prune_old_nodes()
        
        return node_id
    
    def _prune_old_nodes(self):
        """Prune old nodes to manage memory while preserving important context"""
        if len(self.nodes) <= self.max_nodes:
            return
        
        # Sort nodes by importance score and timestamp
        sorted_nodes = sorted(
            self.nodes.values(), 
            key=lambda x: (x.importance_score, x.timestamp), 
            reverse=True
        )
        
        # Keep the most important nodes
        nodes_to_keep = sorted_nodes[:self.max_nodes]
        nodes_to_delete = set(self.nodes.keys()) - set(node.id for node in nodes_to_keep)
        
        # Remove deleted nodes
        for node_id in nodes_to_delete:
            del self.nodes[node_id]
            # Clean up connections
            if node_id in self.conversation_graph:
                del self.conversation_graph[node_id]
            # Remove references to deleted nodes in other connections
            for connections in self.conversation_graph.values():
                connections[:] = [conn_id for conn_id in connections if conn_id != node_id]
    
    def delete_message(self, node_id: str) -> bool:
        """Delete a specific message from the chat history"""
        if node_id in self.nodes:
            del self.nodes[node_id]
            # Clean up connections
            if node_id in self.conversation_graph:
                del self.conversation_graph[node_id]
            # Remove references to deleted node in other connections
            for connections in self.conversation_graph.values():
                connections[:] = [conn_id for conn_id in connections if conn_id != node_id]
            return True
        return False
    
    def clear_history(self):
        """Clear all chat history"""
        self.nodes.clear()
        self.conversation_graph.clear()
        self.session_id = self._generate_session_id()
    
    def _compress_graph(self, target_nodes: int = 20) -> Dict[str, ChatNode]:
        """Compress the graph by removing low-importance nodes while preserving connections"""
        if len(self.nodes) <= target_nodes:
            return self.nodes.copy()
        
        # Sort nodes by importance score
        sorted_nodes = sorted(self.nodes.values(), key=lambda x: x.importance_score, reverse=True)
        
        # Keep the most important nodes
        compressed_nodes = {}
        for node in sorted_nodes[:target_nodes]:
            compressed_nodes[node.id] = node
            
        # Preserve connections between remaining nodes
        for node_id in compressed_nodes:
            preserved_connections = [
                conn_id for conn_id in self.nodes[node_id].connections 
                if conn_id in compressed_nodes
            ]
            compressed_nodes[node_id].connections = preserved_connections
            
        return compressed_nodes
    
    def get_linear_history(self, max_messages: int = 20) -> List[Dict[str, Any]]:
        """Get chat history as a linear list for context window"""
        if not self.nodes:
            return []
        
        # Compress the graph to manage memory while preserving important context
        compressed_nodes = self._compress_graph(max_messages * 2)  # Keep more nodes for better compression
        
        # Convert to linear history format
        history = []
        
        # Sort by timestamp to maintain conversation order
        sorted_nodes = sorted(
            [node for node in compressed_nodes.values()], 
            key=lambda x: x.timestamp
        )
        
        for node in sorted_nodes:
            history.append({
                "content": node.content,
                "isUser": node.role == 'user',
                "timestamp": node.timestamp,
                "importance": node.importance_score,  # Include importance score
                "keywords": node.keywords  # Include keywords for context
            })
        
        # Return most recent messages, but prioritize important ones
        if len(history) <= max_messages:
            return history
        
        # Sort by importance score and take top messages
        important_messages = sorted(history, key=lambda x: x["importance"], reverse=True)[:max_messages//2]
        recent_messages = history[-(max_messages//2):]
        
        # Combine and sort by timestamp
        combined = important_messages + recent_messages
        return sorted(combined, key=lambda x: x["timestamp"])[-max_messages:]
    
    def save_to_file(self):
        """Save the chat history graph to a compressed binary file"""
        try:
            # Convert nodes to serializable format
            serializable_nodes = {
                node_id: asdict(node) 
                for node_id, node in self.nodes.items()
            }
            
            # Create data structure for storage
            data = {
                "session_id": self.session_id,
                "nodes": serializable_nodes,
                "conversation_graph": dict(self.conversation_graph),
                "timestamp": datetime.now().isoformat()
            }
            
            # Serialize and compress with higher compression level for better space efficiency
            json_data = json.dumps(data, separators=(',', ':'))
            compressed_data = zlib.compress(json_data.encode('utf-8'), level=9)  # Maximum compression
            
            # Save to file
            with open(self.storage_path, 'wb') as f:
                f.write(compressed_data)
                
        except Exception as e:
            print(f"Error saving chat history graph: {e}")
    
    def load_from_file(self):
        """Load the chat history graph from a compressed binary file"""
        try:
            if not os.path.exists(self.storage_path):
                return
            
            # Load and decompress
            with open(self.storage_path, 'rb') as f:
                compressed_data = f.read()
            
            json_data = zlib.decompress(compressed_data).decode('utf-8')
            data = json.loads(json_data)
            
            # Restore session ID
            self.session_id = data.get("session_id", self._generate_session_id())
            
            # Restore nodes
            self.nodes = {}
            for node_id, node_data in data.get("nodes", {}).items():
                # Handle the case where keywords and embedding might be missing
                if "keywords" not in node_data:
                    node_data["keywords"] = []
                if "embedding" not in node_data:
                    node_data["embedding"] = []
                self.nodes[node_id] = ChatNode(**node_data)
            
            # Restore conversation graph
            self.conversation_graph = defaultdict(list)
            for node_id, connections in data.get("conversation_graph", {}).items():
                self.conversation_graph[node_id] = connections
                
        except Exception as e:
            print(f"Error loading chat history graph: {e}")

# Global instance for the application
chat_history_manager = GraphBasedChatHistory()

def add_chat_message(content: str, role: str, connections: Optional[List[str]] = None) -> str:
    """Add a chat message to the history manager"""
    return chat_history_manager.add_message(content, role, connections)

def get_chat_history(max_messages: int = 20) -> List[Dict[str, Any]]:
    """Get the chat history as a linear list"""
    return chat_history_manager.get_linear_history(max_messages)

def save_chat_history():
    """Save the chat history to persistent storage"""
    chat_history_manager.save_to_file()

def load_chat_history():
    """Load the chat history from persistent storage"""
    chat_history_manager.load_from_file()

def get_session_info() -> Dict[str, Any]:
    """Get information about the current chat session"""
    return {
        "session_id": chat_history_manager.session_id,
        "node_count": len(chat_history_manager.nodes),
        "graph_connections": sum(len(conns) for conns in chat_history_manager.conversation_graph.values())
    }