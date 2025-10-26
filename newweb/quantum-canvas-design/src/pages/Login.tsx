import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { Sparkles, User, LogIn, Shield } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { AnimatedBackground } from "@/components/AnimatedBackground";
import { useAuth } from "@/contexts/AuthContext";
import { toast } from "sonner";
import { validateAndSanitizeUsername } from "@/lib/utils";

const Login = () => {
  const [username, setUsername] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [loginAttempts, setLoginAttempts] = useState(0);
  const { login, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const loginFormRef = useRef<HTMLFormElement>(null);

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      navigate("/");
    }
  }, [isAuthenticated, navigate]);

  // Implement rate limiting
  useEffect(() => {
    if (loginAttempts >= 5) {
      toast.error("Too many login attempts. Please try again later.");
      const timer = setTimeout(() => {
        setLoginAttempts(0);
        toast.info("You can now try logging in again.");
      }, 60000); // 1 minute cooldown
      return () => clearTimeout(timer);
    }
  }, [loginAttempts]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!username.trim()) {
      toast.error("Please enter a username");
      return;
    }

    // Rate limiting check
    if (loginAttempts >= 5) {
      toast.error("Too many login attempts. Please try again later.");
      return;
    }

    setIsLoading(true);
    setLoginAttempts(prev => prev + 1);

    try {
      // Client-side sanitization before sending to backend
      const sanitizedUsername = validateAndSanitizeUsername(username);
      
      const result = await login(sanitizedUsername);
      
      if (result.success) {
        toast.success("Welcome to OpenManus!");
        setLoginAttempts(0); // Reset on successful login
        navigate("/");
      } else {
        toast.error(result.error || "Login failed");
      }
    } catch (error) {
      toast.error("Login failed. Please try again.");
      console.error("[LOGIN] Error:", error);
    }
    
    setIsLoading(false);
  };

  // Handle form submission on Enter key
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      loginFormRef.current?.requestSubmit();
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background overflow-hidden relative">
      <AnimatedBackground />

      <div className="w-full max-w-md px-6 relative z-10">
        <div className="glass rounded-3xl p-8 shadow-lg glow-primary animate-fade-in-up">
          {/* Logo */}
          <div className="flex justify-center mb-8">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-primary to-secondary flex items-center justify-center glow-primary animate-pulse-glow">
              <Sparkles className="h-8 w-8 text-primary-foreground" />
            </div>
          </div>

          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold gradient-text mb-2">Welcome to OpenManus</h1>
            <p className="text-muted-foreground">Advanced AI Agent Platform</p>
          </div>

          {/* Security Notice */}
          <div className="mb-6 p-3 rounded-lg bg-yellow-500/10 border border-yellow-500/20 flex items-start gap-2">
            <Shield className="h-5 w-5 text-yellow-500 flex-shrink-0 mt-0.5" />
            <p className="text-xs text-yellow-500">
              Enhanced security enabled. All inputs are sanitized and validated.
            </p>
          </div>

          {/* Login Form */}
          <form ref={loginFormRef} onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="username" className="text-sm font-medium">
                Username
              </Label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
                <Input
                  id="username"
                  type="text"
                  placeholder="Enter your username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  onKeyDown={handleKeyDown}
                  className="pl-10 h-12 glass border-border/50 focus:border-primary transition-all"
                  disabled={isLoading || loginAttempts >= 5}
                  maxLength={20}
                  autoComplete="username"
                />
              </div>
              <p className="text-xs text-muted-foreground">
                2-20 characters, letters, numbers, underscores, and hyphens only
              </p>
            </div>

            <Button
              type="submit"
              className="w-full h-12 text-base bg-gradient-to-br from-primary to-secondary hover:opacity-90 transition-all glow-primary"
              disabled={isLoading || loginAttempts >= 5}
            >
              {isLoading ? (
                <div className="flex items-center gap-2">
                  <div className="w-5 h-5 border-2 border-primary-foreground border-t-transparent rounded-full animate-spin" />
                  <span>Logging in...</span>
                </div>
              ) : loginAttempts >= 5 ? (
                <div className="flex items-center gap-2">
                  <Shield className="h-5 w-5" />
                  <span>Rate Limited</span>
                </div>
              ) : (
                <div className="flex items-center gap-2">
                  <LogIn className="h-5 w-5" />
                  <span>Continue</span>
                </div>
              )}
            </Button>
          </form>

          {/* Info */}
          <div className="mt-6 p-4 rounded-xl bg-muted/30 border border-border/30">
            <p className="text-xs text-muted-foreground text-center">
              Your session is secured with enhanced validation. Sessions expire after 24 hours.
            </p>
          </div>
        </div>

        {/* Footer */}
        <p className="text-center text-sm text-muted-foreground mt-6">
          Powered by OpenManus AI Agent Technology • Enhanced Security Mode
        </p>
      </div>
    </div>
  );
};

export default Login;