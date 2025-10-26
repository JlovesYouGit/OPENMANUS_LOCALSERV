import { useState } from "react";
import { Menu, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useAuth } from "@/contexts/AuthContext";
import { cn } from "@/lib/utils";

export const Header = () => {
  const [isConnected] = useState(true);
  const { isAuthenticated } = useAuth();

  return (
    <header className="h-16 border-b border-border/50 bg-card/50 backdrop-blur-xl sticky top-0 z-50">
      <div className="h-full px-4 md:px-6 flex items-center justify-between max-w-7xl mx-auto">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" className="md:hidden">
            <Menu className="h-5 w-5" />
          </Button>
          
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-secondary flex items-center justify-center glow-primary animate-pulse-glow">
              <Sparkles className="h-4 w-4 text-primary-foreground" />
            </div>
            <div className="hidden md:block">
              <h1 className="text-lg font-semibold gradient-text">OpenManus</h1>
              <p className="text-xs text-muted-foreground">Advanced AI Agent Platform</p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <Badge
            variant={isConnected ? "outline" : "destructive"}
            className={cn(
              "hidden sm:flex",
              isConnected && "border-[hsl(var(--tool-success))] text-[hsl(var(--tool-success))]"
            )}
          >
            <div className={cn("w-2 h-2 rounded-full mr-2", isConnected ? "bg-[hsl(var(--tool-success))] animate-pulse" : "bg-destructive")} />
            {isConnected ? "Connected" : "Disconnected"}
          </Badge>
          
          <Button variant="outline" size="sm" className="hidden md:flex glass hover-lift">
            Sign In
          </Button>
          <Button size="sm" className="bg-gradient-to-br from-primary to-secondary hover:opacity-90 transition-all glow-primary">
            {isAuthenticated ? "New Chat" : "Get Started"}
          </Button>
        </div>
      </div>

      {/* Ambient glow effect */}
      <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-primary to-transparent opacity-50" />
    </header>
  );
};

