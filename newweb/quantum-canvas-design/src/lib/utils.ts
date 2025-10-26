export function cn(...inputs: (string | undefined | null | boolean)[]) {
  return inputs.filter(Boolean).join(" ");
}

/**
 * Sanitize user input to prevent XSS attacks
 * @param input - User input string
 * @returns Sanitized string
 */
export function sanitizeInput(input: string): string {
  // Remove or escape potentially dangerous characters
  return input
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#x27;")
    .replace(/\//g, "&#x2F;")
    .trim();
}

/**
 * Validate and sanitize username
 * @param username - Raw username input
 * @returns Sanitized and validated username
 */
export function validateAndSanitizeUsername(username: string): string {
  // First sanitize to prevent XSS
  const sanitized = sanitizeInput(username);
  
  // Then validate length and characters
  if (sanitized.length < 2) {
    throw new Error("Username must be at least 2 characters");
  }
  
  if (sanitized.length > 20) {
    throw new Error("Username must be less than 20 characters");
  }
  
  // Check for allowed characters only
  if (!/^[a-zA-Z0-9_-]+$/.test(sanitized)) {
    throw new Error("Username can only contain letters, numbers, underscores, and hyphens");
  }
  
  return sanitized;
}