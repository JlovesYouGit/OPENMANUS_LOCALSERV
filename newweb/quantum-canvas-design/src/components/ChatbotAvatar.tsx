import { Sparkles, Hand, Smile } from "lucide-react";
import { cn } from "@/lib/utils";

interface ChatbotAvatarProps {
  state: "idle" | "processing" | "responding";
  className?: string;
}

export const ChatbotAvatar = ({ state, className }: ChatbotAvatarProps) => {
  return (
    <div
      className={cn(
        "flex-shrink-0 w-10 h-10 rounded-lg bg-gradient-to-br from-primary to-secondary flex items-center justify-center glow-primary relative overflow-hidden",
        state === "processing" && "animate-pulse-glow",
        className
      )}
    >
      {/* Background shimmer effect - more subtle */}
      <div
        className={cn(
          "absolute inset-0 opacity-0 transition-opacity duration-500 rounded-lg",
          state === "processing" && "opacity-70"
        )}
        style={{
          background: "linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent)",
          animation: state === "processing" ? "shimmer 3s infinite" : "none",
        }}
      />

      {/* Icon based on state */}
      {state === "idle" && (
        <Sparkles className="h-5 w-5 text-primary-foreground animate-fade-in-up" />
      )}
      {state === "processing" && (
        <Hand className="h-5 w-5 text-primary-foreground animate-bounce" style={{ animationDuration: "1.5s" }} />
      )}
      {state === "responding" && (
        <Smile className="h-5 w-5 text-primary-foreground animate-fade-in-up" />
      )}

      <style>{`
        @keyframes shimmer {
          0% {
            transform: translateX(-100%);
          }
          100% {
            transform: translateX(100%);
          }
        }
      `}</style>
    </div>
  );
};