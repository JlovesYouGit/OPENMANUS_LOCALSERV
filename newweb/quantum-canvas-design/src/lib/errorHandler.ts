/**
 * Enhanced error handling utilities for OpenManus
 */

export interface EnhancedError extends Error {
  code?: string;
  details?: string;
  retryable?: boolean;
  timestamp?: number;
}

/**
 * Parse and sanitize JSON responses
 * @param jsonString - Raw JSON string
 * @returns Parsed object or null if invalid
 */
export function parseJSONResponse(jsonString: string): any {
  try {
    // First, try to parse as JSON
    const parsed = JSON.parse(jsonString);
    
    // Validate that it's a proper object
    if (parsed === null || typeof parsed !== 'object' || Array.isArray(parsed)) {
      throw new Error('Invalid JSON structure');
    }
    
    return parsed;
  } catch (error) {
    console.error('[ERROR_HANDLER] JSON parsing failed:', error);
    
    // Try to extract valid JSON from malformed response
    try {
      // Look for JSON-like patterns in the string
      const jsonPattern = /\{[^{}]*\}/g;
      const matches = jsonString.match(jsonPattern);
      
      if (matches && matches.length > 0) {
        // Try parsing the last match (most likely to be complete)
        for (let i = matches.length - 1; i >= 0; i--) {
          try {
            const parsed = JSON.parse(matches[i]);
            if (parsed && typeof parsed === 'object') {
              console.warn('[ERROR_HANDLER] Recovered JSON from malformed response');
              return parsed;
            }
          } catch (innerError) {
            // Continue to next match
          }
        }
      }
    } catch (recoveryError) {
      console.error('[ERROR_HANDLER] JSON recovery failed:', recoveryError);
    }
    
    // Return null for completely invalid JSON
    return null;
  }
}

/**
 * Handle search engine errors with enhanced retry logic
 * @param error - The error object
 * @param attempt - Current retry attempt number
 * @param maxRetries - Maximum retry attempts
 * @returns Enhanced error object with retry information
 */
export function handleSearchError(error: any, attempt: number, maxRetries: number): EnhancedError {
  const enhancedError: EnhancedError = {
    name: error.name || 'SearchError',
    message: error.message || 'Unknown search error occurred',
    timestamp: Date.now(),
    retryable: attempt < maxRetries
  };

  // Add specific error codes based on error type
  if (error.name === 'DuckDuckGoSearchException') {
    enhancedError.code = 'DDG_SEARCH_FAILED';
    enhancedError.details = 'DuckDuckGo search engine is temporarily unavailable';
    enhancedError.retryable = true; // DuckDuckGo errors are often temporary
  } else if (error.name === 'GoogleSearchException') {
    enhancedError.code = 'GOOGLE_SEARCH_FAILED';
    enhancedError.details = 'Google search engine returned an error';
    enhancedError.retryable = attempt < 2; // Limit retries for Google
  } else if (error.name === 'BingSearchException') {
    enhancedError.code = 'BING_SEARCH_FAILED';
    enhancedError.details = 'Bing search engine returned an error';
    enhancedError.retryable = true;
  } else if (error.name === 'BaiduSearchException') {
    enhancedError.code = 'BAIDU_SEARCH_FAILED';
    enhancedError.details = 'Baidu search engine returned an error';
    enhancedError.retryable = true;
  } else if (error.message && error.message.includes('timeout')) {
    enhancedError.code = 'SEARCH_TIMEOUT';
    enhancedError.details = 'Search request timed out';
    enhancedError.retryable = true;
  } else if (error.message && error.message.includes('network')) {
    enhancedError.code = 'NETWORK_ERROR';
    enhancedError.details = 'Network connectivity issue';
    enhancedError.retryable = true;
  } else {
    enhancedError.code = 'UNKNOWN_SEARCH_ERROR';
    enhancedError.details = 'An unexpected error occurred during search';
  }

  // Add error to console with enhanced information
  console.error(`[SEARCH_ERROR] Attempt ${attempt}/${maxRetries}:`, enhancedError);

  return enhancedError;
}

/**
 * Format error for user display
 * @param error - Enhanced error object
 * @returns User-friendly error message
 */
export function formatErrorForUser(error: EnhancedError): string {
  if (!error) {
    return 'An unknown error occurred';
  }

  // Special handling for specific error types
  switch (error.code) {
    case 'DDG_SEARCH_FAILED':
      return '🔍 DuckDuckGo search is temporarily unavailable. Trying alternative search engines...';
    case 'GOOGLE_SEARCH_FAILED':
      return '🔍 Google search encountered an issue. Trying alternative search engines...';
    case 'BING_SEARCH_FAILED':
      return '🔍 Bing search encountered an issue. Trying alternative search engines...';
    case 'BAIDU_SEARCH_FAILED':
      return '🔍 Baidu search encountered an issue. Trying alternative search engines...';
    case 'SEARCH_TIMEOUT':
      return '⏰ Search request timed out. Retrying...';
    case 'NETWORK_ERROR':
      return '🌐 Network connectivity issue. Please check your connection.';
    case 'INVALID_JSON':
      return '📄 Received malformed response from server. Retrying...';
    default:
      return `⚠️ ${error.message || 'An error occurred'}`;
  }
}

/**
 * Create a delay for retry attempts with exponential backoff
 * @param attempt - Current attempt number
 * @param baseDelay - Base delay in milliseconds
 * @returns Promise that resolves after delay
 */
export function createRetryDelay(attempt: number, baseDelay: number = 1000): Promise<void> {
  const delay = Math.min(baseDelay * Math.pow(2, attempt), 30000); // Max 30 seconds
  console.log(`[RETRY] Waiting ${delay}ms before retry attempt ${attempt + 1}`);
  return new Promise(resolve => setTimeout(resolve, delay));
}

/**
 * Validate tool response format
 * @param response - Tool response object
 * @returns Boolean indicating if response is valid
 */
export function validateToolResponse(response: any): boolean {
  if (!response) {
    return false;
  }

  // Check for required fields
  if (typeof response !== 'object') {
    return false;
  }

  // If it has success field, validate it
  if ('success' in response) {
    return typeof response.success === 'boolean';
  }

  // If it has status field, validate it
  if ('status' in response) {
    return typeof response.status === 'string';
  }

  // If it has results field, validate it
  if ('results' in response) {
    return Array.isArray(response.results) || response.results === null;
  }

  // If it has output field, it's likely valid
  if ('output' in response) {
    return typeof response.output === 'string' || response.output === null;
  }

  // If it has error field, it's likely valid
  if ('error' in response) {
    return typeof response.error === 'string' || response.error === null;
  }

  // For other cases, check if it's a valid object
  return Object.keys(response).length > 0;
}

/**
 * Sanitize tool response to prevent XSS
 * @param response - Tool response object
 * @returns Sanitized response
 */
export function sanitizeToolResponse(response: any): any {
  if (typeof response === 'string') {
    // Sanitize string responses
    return response
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#x27;')
      .replace(/\//g, '&#x2F;');
  } else if (Array.isArray(response)) {
    // Recursively sanitize array elements
    return response.map(item => sanitizeToolResponse(item));
  } else if (response && typeof response === 'object') {
    // Recursively sanitize object properties
    const sanitized: any = {};
    for (const [key, value] of Object.entries(response)) {
      sanitized[key] = sanitizeToolResponse(value);
    }
    return sanitized;
  }
  
  // Return primitive values as-is
  return response;
}