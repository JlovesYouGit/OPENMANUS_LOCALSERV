import { useState, useRef, useEffect } from "react";
import { Send, Terminal, Zap, CheckCircle2, AlertCircle, RefreshCw, Wifi, WifiOff } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { cn } from "@/lib/utils";
import { ChatStorage, Message, Chat } from "@/lib/chatStorage";
import { useAuth } from "@/contexts/AuthContext";
import { ChatbotAvatar } from "@/components/ChatbotAvatar";
import { toast } from "sonner";
import { sendMessage, getChatHistory, convertHistoryToMessages, getQueryResult } from "@/services/api";
import { formatErrorForUser } from "@/lib/errorHandler";

interface ChatInterfaceProps {
  currentChatId: string | null;
  onChatUpdate: () => void;
}

export const ChatInterface = ({ currentChatId, onChatUpdate }: ChatInterfaceProps) => {
  const { username } = useAuth();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [botState, setBotState] = useState<"idle" | "processing" | "responding">("idle");
  const [isOnline, setIsOnline] = useState(true);
  const [retryCount, setRetryCount] = useState(0);
  const scrollRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [currentChat, setCurrentChat] = useState<Chat | null>(null);
  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const processingTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Load chat when currentChatId changes
  useEffect(() => {
    if (!username) return;

    if (currentChatId) {
      const chat = ChatStorage.getChat(username, currentChatId);
      if (chat) {
        setCurrentChat(chat);
        setMessages(chat.messages);
        console.log(`[CHAT] Loaded chat ${currentChatId} with ${chat.messages.length} messages`);
      } else {
        // Create new chat if not found
        const welcomeMessage: Message = {
          id: "welcome",
          type: "agent",
          content: `Hello ${username}! I'm OpenManus, your advanced AI agent. I can help you with complex tasks using various tools and capabilities. What can I help you with today?`,
          timestamp: new Date(),
          quality: "high",
        };
        const newChat = ChatStorage.createNewChat(username, welcomeMessage);
        ChatStorage.saveChat(username, newChat);
        setCurrentChat(newChat);
        setMessages([welcomeMessage]);
        onChatUpdate();
        console.log(`[CHAT] Created new chat ${newChat.id}`);
      }
    }
  }, [currentChatId, username, onChatUpdate]);

  // Removed backend history loading on component mount to prevent showing previous messages
  // This was causing the chat to show previous conversation responses on startup
  // Backend history is loaded when a specific chat is selected

  // Setup real-time polling for updates
  useEffect(() => {
    // Clear any existing interval
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current);
    }

    // Start polling for updates every 5 seconds
    pollingIntervalRef.current = setInterval(async () => {
      try {
        // Check connectivity using the stats endpoint which should always be available
        const response = await fetch('/api/stats');
        const newOnlineStatus = response.ok;
        setIsOnline(newOnlineStatus);
        
        // If we were processing and are now offline, reset the processing state
        if (isTyping && !newOnlineStatus) {
          setIsTyping(false);
          setBotState("idle");
          // Clear any existing timeout
          if (processingTimeoutRef.current) {
            clearTimeout(processingTimeoutRef.current);
            processingTimeoutRef.current = null;
          }
        }
      } catch (error) {
        const newOnlineStatus = false;
        setIsOnline(newOnlineStatus);
        // If we were processing and are now offline, reset the processing state
        if (isTyping) {
          setIsTyping(false);
          setBotState("idle");
          // Clear any existing timeout
          if (processingTimeoutRef.current) {
            clearTimeout(processingTimeoutRef.current);
            processingTimeoutRef.current = null;
          }
        }
      }
    }, 5000);

    // Cleanup interval on unmount
    return () => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
      }
      // Clear any existing timeout
      if (processingTimeoutRef.current) {
        clearTimeout(processingTimeoutRef.current);
      }
    };
  }, [isTyping]);

  // Handle online/offline status
  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);
      toast.success("Connection restored");
    };

    const handleOffline = () => {
      setIsOnline(false);
      toast.error("Connection lost");
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isTyping]);

  const handleSend = async () => {
    if (!input.trim() || !username || !currentChat) return;

    // Validate input length
    if (input.trim().length > 1000) {
      toast.error("Message too long. Please limit to 1000 characters.");
      return;
    }

    const userMessage: Message = {
      id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      type: "user",
      content: input.trim(),
      timestamp: new Date(),
    };

    const updatedMessages = [...messages, userMessage];
    setMessages(updatedMessages);
    setInput("");
    setIsTyping(true);
    setBotState("processing");

    // Clear any existing timeout
    if (processingTimeoutRef.current) {
      clearTimeout(processingTimeoutRef.current);
    }

    // Set a timeout to prevent messages from getting stuck in processing state
    processingTimeoutRef.current = setTimeout(() => {
      if (isTyping) {
        setIsTyping(false);
        setBotState("idle");
        toast.error("Request timed out. Please try again.");
      }
      processingTimeoutRef.current = null;
    }, 60000); // 60 second timeout

    // Save user message locally
    const updatedChat = { ...currentChat, messages: updatedMessages };
    ChatStorage.saveChat(username, updatedChat);

    // Auto-update chat title from first user message
    if (currentChat.title === "New Conversation" && input.trim()) {
      const title = input.trim().substring(0, 50) + (input.length > 50 ? "..." : "");
      ChatStorage.updateChatTitle(username, currentChat.id, title);
      onChatUpdate();
    }

    try {
      // Send message to backend API
      const response = await sendMessage(input.trim());
      
      // Clear the timeout since we got a response
      if (processingTimeoutRef.current) {
        clearTimeout(processingTimeoutRef.current);
        processingTimeoutRef.current = null;
      }
      
      if (response.success) {
        // Check if this is a queued request
        if (response.queued && response.query_id) {
          // Poll for the result
          const pollResult = await getQueryResult(response.query_id);
          
          if (pollResult.success && pollResult.status === "completed") {
            const agentMessage: Message = {
              id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
              type: "agent",
              content: pollResult.response || "I have processed your request.",
              timestamp: new Date(),
              quality: pollResult.quality ? "high" : "medium",
            };
            
            // Add tool usage message if provided
            let finalMessages = [...updatedMessages, agentMessage];
            if (pollResult.tool_usage) {
              const toolMessage: Message = {
                id: `tool_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
                type: "tool",
                content: pollResult.tool_usage,
                timestamp: new Date(),
                toolName: "WebSearch",
              };
              finalMessages = [...updatedMessages, toolMessage, agentMessage];
            }
            
            setMessages(finalMessages);
            
            // Save agent message locally
            const finalChat = { ...currentChat, messages: finalMessages };
            ChatStorage.saveChat(username, finalChat);
            onChatUpdate();
          } else {
            // Handle polling error
            const errorMessage: Message = {
              id: `error_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
              type: "agent",
              content: pollResult.error || "Sorry, I encountered an error processing your request.",
              timestamp: new Date(),
              quality: "low",
            };
            
            const finalMessages = [...updatedMessages, errorMessage];
            setMessages(finalMessages);
            
            // Save error message locally
            const finalChat = { ...currentChat, messages: finalMessages };
            ChatStorage.saveChat(username, finalChat);
            onChatUpdate();
            
            // Show user-friendly error message
            toast.error(formatErrorForUser({
              name: "Query Error",
              message: pollResult.error || "Unknown error during query processing",
              code: "QUERY_ERROR",
              timestamp: Date.now()
            }));
          }
        } else {
          // Handle immediate response
          const agentMessage: Message = {
            id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
            type: "agent",
            content: response.response || "I have processed your request.",
            timestamp: new Date(),
            quality: response.quality ? "high" : "medium",
          };
          
          // Add tool usage message if provided
          let finalMessages = [...updatedMessages, agentMessage];
          if (response.tool_usage) {
            const toolMessage: Message = {
              id: `tool_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
              type: "tool",
              content: response.tool_usage,
              timestamp: new Date(),
              toolName: "WebSearch",
            };
            finalMessages = [...updatedMessages, toolMessage, agentMessage];
          }
          
          setMessages(finalMessages);
          
          // Save agent message locally
          const finalChat = { ...currentChat, messages: finalMessages };
          ChatStorage.saveChat(username, finalChat);
          onChatUpdate();
        }
        
        // Reset retry count on success
        setRetryCount(0);
      } else {
        // Handle error response with better user feedback
        console.error("API Error Response:", response);
        const errorMessage: Message = {
          id: `error_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
          type: "agent",
          content: response.error || "Sorry, I encountered an error processing your request.",
          timestamp: new Date(),
          quality: "low",
        };
        
        const finalMessages = [...updatedMessages, errorMessage];
        setMessages(finalMessages);
        
        // Save error message locally
        const finalChat = { ...currentChat, messages: finalMessages };
        ChatStorage.saveChat(username, finalChat);
        onChatUpdate();
        
        // Show user-friendly error message
        toast.error(formatErrorForUser({
          name: "API Error",
          message: response.error || "Unknown error",
          code: response.error?.includes("search") ? "SEARCH_ERROR" : "API_ERROR",
          timestamp: Date.now()
        }));
      }
    } catch (error) {
      console.error("Network Error:", error);
      // Handle network error
      const errorMessage: Message = {
        id: `error_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        type: "agent",
        content: "Sorry, I'm having trouble connecting to the server. Please try again.",
        timestamp: new Date(),
        quality: "low",
      };
      
      const finalMessages = [...updatedMessages, errorMessage];
      setMessages(finalMessages);
      
      // Save error message locally
      const finalChat = { ...currentChat, messages: finalMessages };
      ChatStorage.saveChat(username, finalChat);
      onChatUpdate();
      
      // Show connection error
      toast.error("Connection failed. Please check your network connection.");
    } finally {
      setIsTyping(false);
      setBotState("idle");
      console.log(`[CHAT] Saved messages to chat ${currentChat.id}`);
    }
  };

  const handleRetry = async () => {
    if (retryCount < 3) {
      setRetryCount(prev => prev + 1);
      toast.info(`Retrying... (${retryCount + 1}/3)`);
      // In a real implementation, this would retry the last failed operation
    } else {
      toast.error("Maximum retry attempts reached");
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const getQualityIcon = (quality?: string) => {
    switch (quality) {
      case "high":
        return <CheckCircle2 className="h-3 w-3 text-[hsl(var(--tool-success))]" />;
      case "medium":
        return <AlertCircle className="h-3 w-3 text-[hsl(var(--tool-warning))]" />;
      case "low":
        return <AlertCircle className="h-3 w-3 text-destructive" />;
      default:
        return null;
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Connection Status Bar */}
      <div className={`flex items-center justify-between px-4 py-2 text-xs ${
        isOnline ? "bg-green-500/10 text-green-500" : "bg-red-500/10 text-red-500"
      }`}>
        <div className="flex items-center gap-2">
          {isOnline ? (
            <Wifi className="h-3 w-3" />
          ) : (
            <WifiOff className="h-3 w-3" />
          )}
          <span>{isOnline ? "Connected" : "Disconnected"}</span>
        </div>
        {!isOnline && (
          <Button 
            variant="ghost" 
            size="sm" 
            onClick={handleRetry}
            className="h-6 px-2 text-xs"
          >
            <RefreshCw className="h-3 w-3 mr-1" />
            Retry
          </Button>
        )}
      </div>

      {/* Messages Area */}
      <ScrollArea className="flex-1 px-4 md:px-8" ref={scrollRef}>
        <div className="max-w-4xl mx-auto py-8 space-y-6">
          {messages.map((message, index) => (
            <div
              key={message.id}
              className={cn(
                "animate-fade-in-up flex gap-4",
                message.type === "user" ? "justify-end" : "justify-start"
              )}
              style={{ animationDelay: `${index * 0.1}s` }}
            >
              {message.type !== "user" && (
                <ChatbotAvatar state="idle" />
              )}

              <div
                className={cn(
                  "flex flex-col gap-2 max-w-[80%] md:max-w-[70%]",
                  message.type === "user" ? "items-end" : "items-start"
                )}
              >
                <div
                  className={cn(
                    "rounded-2xl px-6 py-4 shadow-lg transition-all hover-lift",
                    message.type === "user"
                      ? "bg-gradient-to-br from-primary to-secondary text-primary-foreground glow-primary"
                      : message.type === "tool"
                      ? "glass border-[hsl(var(--tool-info))]"
                      : "glass"
                  )}
                >
                  {message.toolName && (
                    <div className="flex items-center gap-2 mb-2">
                      <Terminal className="h-4 w-4 text-[hsl(var(--tool-info))]" />
                      <Badge variant="outline" className="text-xs border-[hsl(var(--tool-info))] text-[hsl(var(--tool-info))]">
                        {message.toolName}
                      </Badge>
                    </div>
                  )}
                  <p className="text-sm md:text-base leading-relaxed whitespace-pre-wrap">
                    {message.content}
                  </p>
                </div>

                <div className="flex items-center gap-2 text-xs text-muted-foreground px-2">
                  <span>{message.timestamp.toLocaleTimeString()}</span>
                  {message.quality && (
                    <div className="flex items-center gap-1">
                      {getQualityIcon(message.quality)}
                      <span className="capitalize">{message.quality} quality</span>
                    </div>
                  )}
                </div>
              </div>

              {message.type === "user" && (
                <div className="flex-shrink-0 w-10 h-10 rounded-lg bg-muted flex items-center justify-center">
                  <div className="h-5 w-5 rounded-full bg-primary" />
                </div>
              )}
            </div>
          ))}

          {isTyping && (
            <div className="flex gap-4 animate-fade-in-up">
              <ChatbotAvatar state={botState} />
              <div className="glass rounded-2xl px-6 py-4 flex items-center gap-3">
                <div className="flex gap-1">
                  <div className="w-2 h-2 rounded-full bg-primary animate-bounce" style={{ animationDelay: "0s" }} />
                  <div className="w-2 h-2 rounded-full bg-primary animate-bounce" style={{ animationDelay: "0.2s" }} />
                  <div className="w-2 h-2 rounded-full bg-primary animate-bounce" style={{ animationDelay: "0.4s" }} />
                </div>
                <span className="text-sm text-muted-foreground">
                  {botState === "processing" ? "Processing..." : "Responding..."}
                </span>
              </div>
            </div>
          )}
        </div>
      </ScrollArea>

      {/* Input Area */}
      <div className="border-t border-border/50 bg-card/50 backdrop-blur-xl">
        <div className="max-w-4xl mx-auto p-4 md:p-6">
          <div className="relative glass rounded-2xl p-4 glow-primary">
            <Textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask OpenManus anything... (Max 1000 characters)"
              className="min-h-[60px] max-h-[200px] bg-transparent border-0 resize-none focus-visible:ring-0 focus-visible:ring-offset-0 text-base pr-24"
              maxLength={1000}
              disabled={!isOnline || isTyping}
            />
            <div className="absolute bottom-4 right-24 text-xs text-muted-foreground">
              {input.length}/1000
            </div>
            <Button
              onClick={handleSend}
              disabled={!input.trim() || isTyping || !isOnline}
              size="icon"
              className="absolute bottom-4 right-4 rounded-xl bg-gradient-to-br from-primary to-secondary hover:opacity-90 transition-all glow-primary disabled:opacity-50"
            >
              <Send className="h-5 w-5" />
            </Button>
          </div>

          <div className="flex items-center justify-between mt-3 px-2">
            <div className="flex items-center gap-3 text-xs text-muted-foreground">
              <div className="flex items-center gap-1">
                <Zap className="h-3 w-3 text-[hsl(var(--tool-success))]" />
                <span>Tools enabled</span>
              </div>
              <div className="h-3 w-px bg-border" />
              <span>Press Enter to send, Shift+Enter for new line</span>
            </div>
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <div className="flex items-center gap-1">
                <div className={`w-2 h-2 rounded-full ${isOnline ? 'bg-green-500' : 'bg-red-500'} animate-pulse`} />
                <span>{isOnline ? 'Online' : 'Offline'}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};