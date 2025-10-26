import { useState, useEffect, useCallback } from "react";
import { MessageSquare, Settings, FileText, Sparkles, ChevronLeft, ChevronRight, Plus, Trash2, LogOut, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogClose } from "@/components/ui/dialog";
import { cn } from "@/lib/utils";
import { ChatStorage, Chat } from "@/lib/chatStorage";
import { useAuth } from "@/contexts/AuthContext";
import { toast } from "sonner";
import { useNavigate } from "react-router-dom";
import { Settings as SettingsComponent } from "@/components/Settings";

interface SidebarProps {
  collapsed: boolean;
  onToggle: () => void;
  currentChatId: string | null;
  onChatSelect: (chatId: string) => void;
  onNewChat: () => void;
  refreshTrigger: number;
}

export const Sidebar = ({ collapsed, onToggle, currentChatId, onChatSelect, onNewChat, refreshTrigger }: SidebarProps) => {
  const { username, logout } = useAuth();
  const navigate = useNavigate();
  const [chats, setChats] = useState<Chat[]>([]);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [chatToDelete, setChatToDelete] = useState<string | null>(null);
  const [settingsOpen, setSettingsOpen] = useState(false);

  // Load chats
  useEffect(() => {
    if (username) {
      const userChats = ChatStorage.getChats(username);
      setChats(userChats.sort((a, b) => b.updatedAt.getTime() - a.updatedAt.getTime()));
      console.log(`[SIDEBAR] Loaded ${userChats.length} chats for ${username}`);
    }
  }, [username, refreshTrigger]);

  const handleDeleteChat = (chatId: string) => {
    setChatToDelete(chatId);
    setDeleteDialogOpen(true);
  };

  const confirmDelete = async () => {
    if (!username || !chatToDelete) return;

    // Delete from local storage
    const success = ChatStorage.deleteChat(username, chatToDelete);
    
    // Also delete from backend
    try {
      const response = await fetch("/api/chat/delete", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ chatId: chatToDelete }),
      });
      
      const data = await response.json();
      if (!data.success) {
        console.error("Failed to delete chat from backend:", data.error);
      }
    } catch (error) {
      console.error("Error deleting chat from backend:", error);
    }

    if (success) {
      toast.success("Chat deleted");
      
      // If deleting current chat, navigate to home/dashboard
      if (chatToDelete === currentChatId) {
        // Clear the current chat selection to show the dashboard
        onChatSelect("");
        // Navigate to the root path to ensure we show the dashboard
        navigate("/");
      }
      
      // Refresh chat list
      const userChats = ChatStorage.getChats(username);
      setChats(userChats.sort((a, b) => b.updatedAt.getTime() - a.updatedAt.getTime()));
    } else {
      toast.error("Failed to delete chat");
    }

    setDeleteDialogOpen(false);
    setChatToDelete(null);
  };

  const handleLogout = () => {
    logout();
    toast.success("Logged out successfully");
    navigate("/login");
  };

  const getRelativeTime = (date: Date) => {
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 1) return "Just now";
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days < 7) return `${days}d ago`;
    return date.toLocaleDateString();
  };

  // Handle ESC key to close settings dialog
  useEffect(() => {
    const handleEscKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && settingsOpen) {
        setSettingsOpen(false);
      }
    };

    document.addEventListener('keydown', handleEscKey);
    return () => {
      document.removeEventListener('keydown', handleEscKey);
    };
  }, [settingsOpen]);

  return (
    <aside
      className={cn(
        "relative h-full bg-sidebar border-r border-sidebar-border transition-all duration-300 flex flex-col",
        collapsed ? "w-16" : "w-64"
      )}
    >
      {/* Header */ }
      <div className="p-4 border-b border-sidebar-border flex items-center justify-between">
        {!collapsed && (
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-secondary flex items-center justify-center glow-primary">
              <Sparkles className="h-4 w-4 text-primary-foreground" />
            </div>
            <span className="font-semibold gradient-text">OpenManus</span>
          </div>
        )}
        <Button
          variant="ghost"
          size="icon"
          onClick={onToggle}
          className={cn("h-8 w-8", collapsed && "mx-auto")}
        >
          {collapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
        </Button>
      </div>

      {/* User Info & New Chat */ }
      <div className="p-4 space-y-3">
        {!collapsed && username && (
          <div className="px-3 py-2 rounded-lg bg-muted/30 border border-border/30">
            <p className="text-xs text-muted-foreground">Logged in as</p>
            <p className="text-sm font-medium truncate">{username}</p>
          </div>
        )}
        
        <Button
          onClick={onNewChat}
          className={cn(
            "w-full bg-gradient-to-br from-primary to-secondary hover:opacity-90 transition-all glow-primary",
            collapsed && "px-0"
          )}
        >
          <Plus className="h-4 w-4" />
          {!collapsed && <span className="ml-2">New Chat</span>}
        </Button>
      </div>

      {/* Chat History */ }
      {!collapsed && (
        <ScrollArea className="flex-1 px-2">
          <div className="space-y-1 py-2">
            {chats.length === 0 ? (
              <div className="px-3 py-8 text-center">
                <p className="text-sm text-muted-foreground">No chat history yet</p>
                <p className="text-xs text-muted-foreground mt-1">Start a new conversation!</p>
              </div>
            ) : (
              chats.map((chat) => (
                <div
                  key={chat.id}
                  className={cn(
                    "relative group rounded-lg transition-all hover-lift",
                    currentChatId === chat.id
                      ? "glass border-primary/30 glow-primary"
                      : "hover:bg-sidebar-accent"
                  )}
                >
                  <button
                    onClick={() => onChatSelect(chat.id)}
                    className="w-full text-left px-3 py-3 pr-10"
                  >
                    <div className="flex items-start gap-2">
                      <MessageSquare className="h-4 w-4 mt-0.5 flex-shrink-0 text-muted-foreground group-hover:text-primary transition-colors" />
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium truncate">{chat.title}</p>
                        <p className="text-xs text-muted-foreground mt-0.5">
                          {getRelativeTime(chat.updatedAt)} · {chat.messages.length} msgs
                        </p>
                      </div>
                    </div>
                  </button>
                  
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDeleteChat(chat.id);
                    }}
                    className="absolute right-2 top-1/2 -translate-y-1/2 h-7 w-7 opacity-0 group-hover:opacity-100 transition-opacity hover:bg-destructive/20 hover:text-destructive"
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                  </Button>
                </div>
              ))
            )}
          </div>
        </ScrollArea>
      )}

      {/* Bottom Navigation */ }
      <div className="border-t border-sidebar-border p-2 space-y-1">
        <Button
          variant="ghost"
          className={cn(
            "w-full justify-start",
            collapsed && "justify-center px-0"
          )}
        >
          <FileText className="h-4 w-4" />
          {!collapsed && <span className="ml-2">Documentation</span>}
        </Button>
        <Button
          variant="ghost"
          onClick={() => setSettingsOpen(true)}
          className={cn(
            "w-full justify-start",
            collapsed && "justify-center px-0"
          )}
        >
          <Settings className="h-4 w-4" />
          {!collapsed && <span className="ml-2">Settings</span>}
        </Button>
        <Button
          variant="ghost"
          onClick={handleLogout}
          className={cn(
            "w-full justify-start text-destructive hover:text-destructive hover:bg-destructive/10",
            collapsed && "justify-center px-0"
          )}
        >
          <LogOut className="h-4 w-4" />
          {!collapsed && <span className="ml-2">Logout</span>}
        </Button>
      </div>

      {/* Delete Confirmation Dialog */ }
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent className="glass">
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Chat</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete this chat? This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={confirmDelete}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
      <Dialog open={settingsOpen} onOpenChange={setSettingsOpen}>
        <DialogContent className="glass">
          <DialogHeader>
            <DialogTitle>Settings</DialogTitle>
            <DialogClose className="absolute right-4 top-4">
              <X className="h-4 w-4" />
            </DialogClose>
          </DialogHeader>
          <SettingsComponent />
        </DialogContent>
      </Dialog>
    </aside>
  );
};