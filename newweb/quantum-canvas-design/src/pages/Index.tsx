import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Header } from "@/components/Header";
import { Sidebar } from "@/components/Sidebar";
import { ChatInterface } from "@/components/ChatInterface";
import { AnimatedBackground } from "@/components/AnimatedBackground";
import { useAuth } from "@/contexts/AuthContext";
import { ChatStorage } from "@/lib/chatStorage";
import { initializeAgent } from "@/services/api";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Plus, Sparkles, MessageSquare, Zap, Cpu } from "lucide-react";

const Index = () => {
  const { isAuthenticated, username } = useAuth();
  const navigate = useNavigate();
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [currentChatId, setCurrentChatId] = useState<string | null>(null);
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [agentInitialized, setAgentInitialized] = useState(false);

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!isAuthenticated) {
      navigate("/login");
    }
  }, [isAuthenticated, navigate]);

  // Initialize agent when component mounts
  useEffect(() => {
    const initAgent = async () => {
      try {
        const response = await initializeAgent();
        if (response.success) {
          setAgentInitialized(true);
          toast.success("Agent initialized successfully!");
        } else {
          toast.error(`Agent initialization failed: ${response.error}`);
        }
      } catch (error) {
        console.error("Error initializing agent:", error);
        toast.error("Failed to initialize agent");
      }
    };

    if (isAuthenticated) {
      initAgent();
    }
  }, [isAuthenticated]);

  // Initialize first chat
  useEffect(() => {
    if (username && !currentChatId) {
      const existingChats = ChatStorage.getChats(username);
      if (existingChats.length > 0) {
        setCurrentChatId(existingChats[0].id);
      } else {
        // Don't automatically create a new chat, let the user decide
      }
    }
  }, [username, currentChatId]);

  const handleNewChat = () => {
    if (!username) return;
    const newChat = ChatStorage.createNewChat(username);
    ChatStorage.saveChat(username, newChat);
    setCurrentChatId(newChat.id);
    setRefreshTrigger((prev) => prev + 1);
  };

  const handleChatSelect = (chatId: string) => {
    // If chatId is empty string, set to null to show dashboard
    setCurrentChatId(chatId || null);
  };

  const handleChatUpdate = () => {
    setRefreshTrigger((prev) => prev + 1);
  };

  if (!isAuthenticated) {
    return null;
  }

  // Show dashboard when no chat is selected
  if (!currentChatId) {
    return (
      <div className="flex flex-col h-screen bg-background overflow-hidden">
        <AnimatedBackground />
        <Header />
        
        <div className="flex flex-1 overflow-hidden relative">
          <Sidebar
            collapsed={sidebarCollapsed}
            onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
            currentChatId={currentChatId}
            onChatSelect={handleChatSelect}
            onNewChat={handleNewChat}
            refreshTrigger={refreshTrigger}
          />
          
          <main className="flex-1 overflow-hidden flex items-center justify-center">
            <div className="text-center max-w-2xl px-4">
              <div className="w-24 h-24 rounded-2xl bg-gradient-to-br from-primary/20 to-secondary/20 flex items-center justify-center mx-auto mb-8 border border-primary/30">
                <Sparkles className="h-12 w-12 text-primary" />
              </div>
              
              <h1 className="text-3xl font-bold bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent mb-4">
                Welcome to OpenManus
              </h1>
              
              <p className="text-lg text-muted-foreground mb-8">
                Your advanced AI agent platform for complex tasks and intelligent workflows.
              </p>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
                <div className="glass p-6 rounded-xl border border-border/50">
                  <MessageSquare className="h-8 w-8 text-primary mb-3 mx-auto" />
                  <h3 className="font-semibold mb-2">Chat Interface</h3>
                  <p className="text-sm text-muted-foreground">
                    Natural conversation with advanced reasoning capabilities
                  </p>
                </div>
                
                <div className="glass p-6 rounded-xl border border-border/50">
                  <Zap className="h-8 w-8 text-primary mb-3 mx-auto" />
                  <h3 className="font-semibold mb-2">Tool Integration</h3>
                  <p className="text-sm text-muted-foreground">
                    Access to web search, code execution, and file operations
                  </p>
                </div>
                
                <div className="glass p-6 rounded-xl border border-border/50">
                  <Cpu className="h-8 w-8 text-primary mb-3 mx-auto" />
                  <h3 className="font-semibold mb-2">Multi-Agent</h3>
                  <p className="text-sm text-muted-foreground">
                    Coordinate multiple specialized agents for complex tasks
                  </p>
                </div>
              </div>
              
              <Button 
                size="lg" 
                className="bg-gradient-to-br from-primary to-secondary hover:opacity-90 transition-all glow-primary px-8 py-6 text-lg"
                onClick={handleNewChat}
              >
                <Plus className="h-5 w-5 mr-2" />
                Start New Chat
              </Button>
              
              <p className="text-sm text-muted-foreground mt-6">
                Select an existing chat from the sidebar or start a new conversation
              </p>
            </div>
          </main>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-screen bg-background overflow-hidden">
      <AnimatedBackground />

      <Header />
      
      <div className="flex flex-1 overflow-hidden relative">
        <Sidebar
          collapsed={sidebarCollapsed}
          onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
          currentChatId={currentChatId}
          onChatSelect={handleChatSelect}
          onNewChat={handleNewChat}
          refreshTrigger={refreshTrigger}
        />
        
        <main className="flex-1 overflow-hidden">
          {currentChatId && (
            <ChatInterface
              currentChatId={currentChatId}
              onChatUpdate={handleChatUpdate}
            />
          )}
        </main>
      </div>
    </div>
  );
};

export default Index;