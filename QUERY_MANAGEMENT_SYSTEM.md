# OpenManus Query Management System

## Overview

The Query Management System is designed to prevent model crashes or overload by queuing incoming messages and processing them asynchronously. It includes message compression to optimize processing speed while maintaining 90% of the original structure, with reconstruction capabilities to ensure accuracy and relevance.

## Key Features

### 1. Query Queuing
- Incoming messages are queued to prevent model overload
- Priority-based queuing system (1-10, higher is more urgent)
- Rate limiting to control concurrent processing
- Configurable queue size limits

### 2. Message Compression
- Light compression techniques to reduce processing overhead
- Maintains 90% of original message structure
- Common word abbreviation mappings
- Whitespace normalization
- Redundant punctuation removal

### 3. Message Reconstruction
- Full reconstruction of original messages before processing
- Maintains accuracy and relevance to user intent
- Preserves semantic meaning

### 4. Asynchronous Processing
- Non-blocking query processing
- Callback-based processing system
- Result storage and retrieval
- Error handling and recovery

## System Architecture

### Core Components

1. **QueryCompressor** - Handles message compression and reconstruction
2. **QueryQueue** - Manages the queue of incoming queries with priority
3. **QueryManager** - Main system orchestrator
4. **Web UI Integration** - Flask endpoint integration for queuing

### Data Flow

1. User submits a message through the web interface
2. Message is queued with appropriate priority
3. Message is compressed for efficient storage
4. Worker thread processes queued queries asynchronously
5. Messages are reconstructed before processing
6. Results are stored for retrieval
7. Web UI polls for results or receives immediate responses for simple queries

## Implementation Details

### Compression Algorithm

The compression algorithm uses several techniques to reduce message size while preserving structure:

1. **Whitespace Normalization**: Reduces multiple spaces to single spaces
2. **Common Word Abbreviation**: Replaces common words with shorter abbreviations
3. **Punctuation Optimization**: Removes redundant punctuation while preserving sentence structure

### Priority System

Priority levels (1-10):
- 8-10: Greetings and very short messages
- 5-7: Standard messages
- 1-4: Very long messages that require more resources

### Rate Limiting

The system limits concurrent processing to prevent resource exhaustion:
- Maximum concurrent processing: 3 queries
- Maximum queue size: 100 queries

## API Endpoints

### POST /api/chat
Submit a chat message for processing:
- Messages are queued for processing
- Simple greetings are processed immediately
- Returns query ID for queued messages

### GET /api/query/{query_id}
Retrieve the result of a queued query:
- Returns processing status
- Returns final result when available

### GET /api/stats
Get system statistics:
- Queue size
- Processing count
- Performance metrics

## Performance Optimizations

1. **Asynchronous Processing**: Non-blocking query handling
2. **Memory Management**: Efficient compression and storage
3. **Priority Queuing**: Important queries processed first
4. **Rate Limiting**: Prevents system overload
5. **Caching**: Results stored for quick retrieval

## Usage Examples

### Python API Usage

```python
from app.utils.query_manager import enqueue_query, get_query_result

# Enqueue a query
query_id = enqueue_query("What is the weather today?", priority=5)

# Check for results
result = get_query_result(query_id)
if result:
    print(f"Result: {result}")
```

### Web API Usage

```javascript
// Submit a query
fetch('/api/chat', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({message: "What is the weather today?"})
})
.then(response => response.json())
.then(data => {
    if (data.queued) {
        // Poll for results
        pollForResult(data.query_id);
    } else {
        // Immediate response
        console.log(data.response);
    }
});
```

## Configuration

The system can be configured through the QueryManager constructor:

```python
query_manager = QueryManager(
    max_queue_size=100,
    max_concurrent_processing=3
)
```

## Monitoring and Statistics

The system provides detailed statistics for monitoring:
- Total queries queued
- Queries processed successfully
- Queries failed
- Average queue time
- Average processing time
- Current queue size
- Processing concurrency

## Error Handling

The system includes comprehensive error handling:
- Queue overflow protection
- Processing error recovery
- Result retrieval timeouts
- Graceful degradation

## Future Enhancements

Planned improvements:
1. Advanced compression algorithms
2. Dynamic priority adjustment based on user behavior
3. Machine learning-based query classification
4. Enhanced monitoring and alerting
5. Distributed processing capabilities