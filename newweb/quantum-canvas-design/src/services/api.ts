import { Message } from "@/lib/chatStorage";
import { sanitizeInput } from "@/lib/utils";
import { 
  parseJSONResponse, 
  handleSearchError, 
  formatErrorForUser, 
  createRetryDelay,
  validateToolResponse,
  sanitizeToolResponse
} from "@/lib/errorHandler";

// API base URL - this should match your Flask backend
const API_BASE_URL = "http://localhost:5000/api";

export interface ChatResponse {
  success: boolean;
  response?: string;
  tool_usage?: string;
  quality?: {
    overall: number;
    relevance: number;
    accuracy: number;
    completeness: number;
  };
  error?: string;
  details?: string;
  // Properties for queued requests
  queued?: boolean;
  query_id?: string;
  priority?: number;
  message?: string;
}

export interface HistoryResponse {
  success: boolean;
  history?: Array<{
    timestamp: string;
    content: string;
    isUser: boolean;
    isTool?: boolean;
  }>;
  error?: string;
  details?: string;
}

export interface InitResponse {
  success: boolean;
  message?: string;
  error?: string;
  details?: string;
}

export interface QueryStatusResponse {
  success: boolean;
  status: "processing" | "completed" | "failed";
  response?: string;
  tool_usage?: string;
  quality?: {
    overall: number;
    relevance: number;
    accuracy: number;
    completeness: number;
  };
  error?: string;
  message?: string;
  details?: string;
}

/**
 * Initialize the agent with retry logic
 */
export async function initializeAgent(maxRetries: number = 3): Promise<InitResponse> {
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      const response = await fetch(`${API_BASE_URL}/init`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
      });
      
      // Try to parse the response
      const textResponse = await response.text();
      const parsedResponse = parseJSONResponse(textResponse);
      
      if (!parsedResponse) {
        throw new Error('Invalid JSON response from server');
      }
      
      return parsedResponse;
    } catch (error) {
      console.error(`[API] Agent initialization attempt ${attempt + 1} failed:`, error);
      
      if (attempt < maxRetries) {
        // Wait before retrying
        await createRetryDelay(attempt, 2000);
      } else {
        return {
          success: false,
          error: "Failed to initialize agent after multiple attempts",
          details: error instanceof Error ? error.message : "Unknown error"
        };
      }
    }
  }
  
  return {
    success: false,
    error: "Agent initialization failed",
    details: "Maximum retry attempts exceeded"
  };
}

/**
 * Send a message to the chat API with enhanced security and error handling
 * @param message The user's message
 */
export async function sendMessage(message: string, maxRetries: number = 3): Promise<ChatResponse> {
  // Validate input
  if (!message || typeof message !== 'string') {
    return {
      success: false,
      error: "Invalid message input"
    };
  }

  // Sanitize input before sending to backend
  const sanitizedMessage = sanitizeInput(message);
  
  // Validate message length
  if (sanitizedMessage.length === 0) {
    return {
      success: false,
      error: "Message cannot be empty"
    };
  }
  
  if (sanitizedMessage.length > 1000) {
    return {
      success: false,
      error: "Message too long. Please limit to 1000 characters."
    };
  }

  // Try sending the message with retry logic
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: 'include',
        body: JSON.stringify({ message: sanitizedMessage }),
      });

      // Check if response is ok
      if (!response.ok) {
        // Try to parse error response
        let errorText = '';
        try {
          errorText = await response.text();
        } catch (e) {
          errorText = `HTTP error! status: ${response.status}`;
        }
        throw new Error(errorText || `HTTP error! status: ${response.status}`);
      }

      // Try to parse the response
      const textResponse = await response.text();
      const parsedResponse = parseJSONResponse(textResponse);
      
      if (!parsedResponse) {
        throw new Error('Invalid JSON response from server');
      }
      
      // Validate the response structure
      if (!validateToolResponse(parsedResponse)) {
        throw new Error('Invalid response structure from server');
      }
      
      // Sanitize the response to prevent XSS
      const sanitizedResponse = sanitizeToolResponse(parsedResponse);
      
      return sanitizedResponse;
    } catch (error) {
      console.error(`[API] Send message attempt ${attempt + 1} failed:`, error);
      
      // If this is the last attempt, return the error
      if (attempt === maxRetries) {
        return {
          success: false,
          error: "Failed to send message after multiple attempts",
          details: error instanceof Error ? error.message : "Unknown error"
        };
      }
      
      // Wait before retrying
      await createRetryDelay(attempt, 3000);
    }
  }
  
  return {
    success: false,
    error: "Message sending failed",
    details: "Maximum retry attempts exceeded"
  };
}

/**
 * Get chat history from the backend with retry logic
 */
export async function getChatHistory(maxRetries: number = 3): Promise<HistoryResponse> {
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      const response = await fetch(`${API_BASE_URL}/history`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
      });
      
      // Try to parse the response
      const textResponse = await response.text();
      const parsedResponse = parseJSONResponse(textResponse);
      
      if (!parsedResponse) {
        throw new Error('Invalid JSON response from server');
      }
      
      return parsedResponse;
    } catch (error) {
      console.error(`[API] Get chat history attempt ${attempt + 1} failed:`, error);
      
      if (attempt < maxRetries) {
        // Wait before retrying
        await createRetryDelay(attempt, 2000);
      } else {
        return {
          success: false,
          error: "Failed to fetch chat history after multiple attempts",
          details: error instanceof Error ? error.message : "Unknown error"
        };
      }
    }
  }
  
  return {
    success: false,
    error: "Chat history fetch failed",
    details: "Maximum retry attempts exceeded"
  };
}

/**
 * Poll for query result by query ID
 * @param queryId The ID of the queued query
 */
export async function getQueryResult(queryId: string, maxRetries: number = 150): Promise<QueryStatusResponse> {
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      const response = await fetch(`${API_BASE_URL}/query/${queryId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
      });
      
      // Check if response is ok
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      // Try to parse the response
      const textResponse = await response.text();
      const parsedResponse = parseJSONResponse(textResponse);
      
      if (!parsedResponse) {
        throw new Error('Invalid JSON response from server');
      }
      
      // If query is completed or failed, return the result
      if (parsedResponse.status === "completed" || parsedResponse.status === "failed") {
        return parsedResponse;
      }
      
      // If still processing, wait before next poll
      if (attempt < maxRetries) {
        // Wait 5 seconds before polling again (increased from 3 seconds to reduce server load)
        await new Promise(resolve => setTimeout(resolve, 5000));
      }
    } catch (error) {
      console.error(`[API] Poll query result attempt ${attempt + 1} failed:`, error);
      
      // If this is the last attempt, return the error
      if (attempt === maxRetries) {
        return {
          success: false,
          status: "failed",
          error: "Failed to poll query result after multiple attempts",
          details: error instanceof Error ? error.message : "Unknown error"
        };
      }
      
      // Wait before retrying (increased from 1 second)
      await createRetryDelay(attempt, 2000);
    }
  }
  
  return {
    success: false,
    status: "failed",
    error: "Query processing timed out after 12.5 minutes",
    details: "Maximum polling attempts exceeded"
  };
}

/**
 * Convert backend history format to frontend message format
 * @param history Backend history response
 */
export function convertHistoryToMessages(history: HistoryResponse["history"]): Message[] {
  if (!history || !Array.isArray(history)) return [];
  
  return history.map((item, index) => {
    // Determine message type
    let type: "user" | "agent" | "tool" = "agent";
    if (item.isTool) {
      type = "tool";
    } else if (item.isUser) {
      type = "user";
    }
    
    return {
      id: `msg_${index}_${Date.now()}`,
      type: type,
      content: item.content || "",
      timestamp: new Date(item.timestamp),
      quality: "high" as "high" | "medium" | "low" // Default quality for historical messages
    };
  }).filter(message => message.content); // Filter out empty messages
}