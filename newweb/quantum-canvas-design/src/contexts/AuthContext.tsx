import { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { z } from "zod";
import { validateAndSanitizeUsername } from "@/lib/utils";

// Validation schema
const usernameSchema = z.string()
  .trim()
  .min(2, "Username must be at least 2 characters")
  .max(20, "Username must be less than 20 characters")
  .regex(/^[a-zA-Z0-9_-]+$/, "Username can only contain letters, numbers, underscores, and hyphens");

interface AuthContextType {
  username: string | null;
  login: (username: string) => Promise<{ success: boolean; error?: string }>;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const AUTH_STORAGE_KEY = "openmanus_username";
const LAST_LOGIN_KEY = "openmanus_last_login";
const SESSION_ID_KEY = "openmanus_session_id";

/**
 * Generate a secure session ID
 * @returns Secure session identifier
 */
function generateSessionId(): string {
  return btoa(`${Date.now()}-${Math.random()}-${crypto?.randomUUID?.() || Math.random()}`).replace(/[^a-zA-Z0-9]/g, '');
}

/**
 * Validate session integrity
 * @param storedSessionId - Stored session ID
 * @returns Whether session is valid
 */
function validateSession(storedSessionId: string | null): boolean {
  if (!storedSessionId) return false;
  
  // In a real implementation, this would check against a server-side session store
  // For now, we'll just verify it exists and has reasonable format
  return storedSessionId.length > 10;
}

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [username, setUsername] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Auto-login from cache with enhanced security
  useEffect(() => {
    const storedUsername = localStorage.getItem(AUTH_STORAGE_KEY);
    const lastLogin = localStorage.getItem(LAST_LOGIN_KEY);
    const sessionId = localStorage.getItem(SESSION_ID_KEY);
    
    if (storedUsername && lastLogin && sessionId) {
      // Validate session integrity
      if (!validateSession(sessionId)) {
        // Clear invalid session
        localStorage.removeItem(AUTH_STORAGE_KEY);
        localStorage.removeItem(LAST_LOGIN_KEY);
        localStorage.removeItem(SESSION_ID_KEY);
        console.log("[AUTH] Invalid session detected, cleared cache");
        setIsLoading(false);
        return;
      }
      
      const loginTime = new Date(lastLogin);
      const now = new Date();
      const hoursSinceLogin = (now.getTime() - loginTime.getTime()) / (1000 * 60 * 60);
      
      // Auto-login if less than 24 hours
      if (hoursSinceLogin < 24) {
        // Additional validation of username
        try {
          validateAndSanitizeUsername(storedUsername);
          setUsername(storedUsername);
          console.log(`[AUTH] Auto-logged in as: ${storedUsername}`);
        } catch (error) {
          // Clear invalid username
          localStorage.removeItem(AUTH_STORAGE_KEY);
          localStorage.removeItem(LAST_LOGIN_KEY);
          localStorage.removeItem(SESSION_ID_KEY);
          console.log("[AUTH] Invalid username in session, cleared cache");
        }
      } else {
        // Clear expired session
        localStorage.removeItem(AUTH_STORAGE_KEY);
        localStorage.removeItem(LAST_LOGIN_KEY);
        localStorage.removeItem(SESSION_ID_KEY);
        console.log("[AUTH] Session expired, cleared cache");
      }
    }
    
    setIsLoading(false);
  }, []);

  const login = async (inputUsername: string): Promise<{ success: boolean; error?: string }> => {
    try {
      // Sanitize and validate username
      const sanitizedUsername = validateAndSanitizeUsername(inputUsername);
      
      // Validate with Zod schema
      const validatedUsername = usernameSchema.parse(sanitizedUsername);
      
      // Generate secure session ID
      const sessionId = generateSessionId();
      
      // Store in localStorage with enhanced security
      localStorage.setItem(AUTH_STORAGE_KEY, validatedUsername);
      localStorage.setItem(LAST_LOGIN_KEY, new Date().toISOString());
      localStorage.setItem(SESSION_ID_KEY, sessionId);
      
      setUsername(validatedUsername);
      console.log(`[AUTH] User logged in: ${validatedUsername} at ${new Date().toISOString()} with session ${sessionId}`);
      
      return { success: true };
    } catch (error) {
      if (error instanceof z.ZodError) {
        return { success: false, error: error.errors[0].message };
      }
      if (error instanceof Error) {
        return { success: false, error: error.message };
      }
      return { success: false, error: "Login failed. Please try again." };
    }
  };

  const logout = () => {
    // Clear all auth-related storage
    localStorage.removeItem(AUTH_STORAGE_KEY);
    localStorage.removeItem(LAST_LOGIN_KEY);
    localStorage.removeItem(SESSION_ID_KEY);
    setUsername(null);
    console.log("[AUTH] User logged out");
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-primary to-secondary flex items-center justify-center animate-pulse-glow">
            <div className="w-6 h-6 border-2 border-primary-foreground border-t-transparent rounded-full animate-spin" />
          </div>
          <p className="text-sm text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <AuthContext.Provider
      value={{
        username,
        login,
        logout,
        isAuthenticated: !!username,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
};