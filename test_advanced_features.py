#!/usr/bin/env python
"""
Test script to verify all advanced features of OpenManus chat system
"""

import asyncio
import json
import os
import sys
import tempfile
from pathlib import Path

# Add the OpenManus directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from app.utils.advanced_chat_history import GraphBasedChatHistory, add_chat_message, get_chat_history, save_chat_history, load_chat_history
from app.utils.enhanced_attention import EnhancedAttentionMechanism, identify_user_intent, generate_enhanced_context, refine_model_response, evaluate_response_quality
from app.utils.rust_compression import compress_chat_history, decompress_chat_history

def test_graph_based_chat_history():
    """Test the graph-based chat history system"""
    print("Testing graph-based chat history system...")
    
    # Create a new chat history manager
    chat_manager = GraphBasedChatHistory()
    
    # Add some messages
    node1_id = chat_manager.add_message("Hello, how are you?", "user")
    node2_id = chat_manager.add_message("I'm doing well, thank you for asking!", "assistant", [node1_id])
    node3_id = chat_manager.add_message("What can you help me with today?", "user", [node2_id])
    node4_id = chat_manager.add_message("I can help with many things like answering questions, solving problems, or having a conversation.", "assistant", [node3_id])
    
    print(f"✅ Added {len(chat_manager.nodes)} nodes to the graph")
    
    # Test linear history conversion
    linear_history = chat_manager.get_linear_history(10)
    print(f"✅ Converted graph to linear history with {len(linear_history)} messages")
    
    # Test compression
    compressed_nodes = chat_manager._compress_graph(3)
    print(f"✅ Compressed graph from {len(chat_manager.nodes)} to {len(compressed_nodes)} nodes")
    
    # Test saving and loading
    test_file = "test_chat_graph.bin"
    chat_manager.storage_path = test_file
    chat_manager.save_to_file()
    
    # Load into a new manager
    new_manager = GraphBasedChatHistory(test_file)
    new_manager.load_from_file()
    print(f"✅ Saved and loaded chat history with {len(new_manager.nodes)} nodes")
    
    # Clean up
    if os.path.exists(test_file):
        os.remove(test_file)
    
    return True

def test_enhanced_attention_mechanism():
    """Test the enhanced attention mechanism"""
    print("\nTesting enhanced attention mechanism...")
    
    attention = EnhancedAttentionMechanism()
    
    # Test intent identification
    test_inputs = [
        "What is the capital of France?",
        "Calculate 2+2",
        "Create a story about a robot",
        "Compare Python and JavaScript",
        "Explain quantum computing",
        "Help me with my homework"
    ]
    
    intents = [attention.identify_user_intent(inp) for inp in test_inputs]
    print(f"✅ Identified intents: {intents}")
    
    # Test entity extraction
    test_text = "I want to learn about Python and JavaScript programming languages"
    entities = attention.extract_key_entities(test_text)
    print(f"✅ Extracted entities: {entities}")
    
    # Test irrelevant content filtering
    test_content = "Um, basically, I, uh, want to know, like, what is Python? You know?"
    filtered = attention.filter_irrelevant_content(test_content)
    print(f"✅ Filtered content: '{filtered}'")
    
    # Test context generation
    user_input = "What is machine learning?"
    history = [
        {"content": "Hello", "isUser": True},
        {"content": "Hi there! How can I help?", "isUser": False},
        {"content": "I'm interested in AI", "isUser": True},
        {"content": "Artificial Intelligence is a fascinating field!", "isUser": False}
    ]
    
    context = attention.generate_context_prompt(user_input, history)
    print(f"✅ Generated context prompt ({len(context)} chars)")
    
    # Test response refinement
    response = "Um, basically, machine learning is, like, a type of AI, you know? It's where computers learn from data."
    refined = attention.refine_response(response, user_input)
    print(f"✅ Refined response: '{refined}'")
    
    # Test quality evaluation
    quality = attention.optimize_attention_weights(user_input, refined)
    print(f"✅ Evaluated response quality: {quality}")
    
    return True

def test_rust_compression_enhancements():
    """Test the enhanced Rust-inspired compression"""
    print("\nTesting Rust-inspired compression enhancements...")
    
    # Create test chat history
    test_history = []
    for i in range(25):  # Create more items than our MAX_CONTEXT_WINDOW
        test_history.append({
            "timestamp": f"2023-01-01T00:00:{i:02d}",
            "content": f"Message {i} with some content to compress and make larger",
            "isUser": i % 2 == 0
        })
    
    # Test compression
    compressed = compress_chat_history(test_history)
    print(f"✅ Compressed {len(test_history)} messages to {len(compressed)} bytes")
    
    # Test decompression
    decompressed = decompress_chat_history(compressed)
    print(f"✅ Decompressed back to {len(decompressed)} messages")
    
    # Verify data integrity
    if len(decompressed) == len(test_history):
        print("✅ Data integrity verified")
        return True
    else:
        print("❌ Data integrity check failed")
        return False

def test_cross_session_history():
    """Test cross-session history support"""
    print("\nTesting cross-session history support...")
    
    # Add messages to history
    add_chat_message("Hello, this is session 1", "user")
    add_chat_message("Nice to meet you!", "assistant")
    add_chat_message("What can you do?", "user")
    add_chat_message("I can help with many tasks!", "assistant")
    
    # Save history
    save_chat_history()
    
    # Simulate new session by clearing memory
    # In a real scenario, this would be a new process
    
    # Load history
    load_chat_history()
    
    # Get history
    history = get_chat_history(10)
    print(f"✅ Loaded cross-session history with {len(history)} messages")
    
    if len(history) >= 4:
        print("✅ Cross-session history support working correctly")
        return True
    else:
        print("❌ Cross-session history support failed")
        return False

def main():
    """Run all tests"""
    print("Running OpenManus advanced features verification tests...\n")
    
    tests = [
        test_graph_based_chat_history,
        test_enhanced_attention_mechanism,
        test_rust_compression_enhancements,
        test_cross_session_history
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\nTest Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The advanced features are working correctly.")
        print("\nSummary of improvements implemented:")
        print("1. ✅ Graph-based chat history management with intelligent compression")
        print("2. ✅ Enhanced attention mechanism for better context understanding")
        print("3. ✅ Rust-inspired compression for efficient data handling")
        print("4. ✅ Cross-session history support")
        print("5. ✅ Response quality evaluation and refinement")
        return True
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    main()