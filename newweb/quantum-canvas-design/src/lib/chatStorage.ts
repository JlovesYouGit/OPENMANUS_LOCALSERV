export interface Message {
  id: string;
  type: "user" | "agent" | "tool";
  content: string;
  timestamp: Date;
  toolName?: string;
  quality?: "high" | "medium" | "low";
}

export interface Chat {
  id: string;
  title: string;
  messages: Message[];
  createdAt: Date;
  updatedAt: Date;
  username: string;
}

const CHATS_STORAGE_[REDACTED];
const CHAT_METADATA_[REDACTED];

// Enhanced metadata for better session management
interface ChatMetadata {
  lastSyncTime: number;
  version: string;
  totalChats: number;
}

export class ChatStorage {
  private static getChatKey(username: string): string {
    return `${CHATS_STORAGE_KEY}_${username}`;
  }

  private static getMetadataKey(username: string): string {
    return `${CHAT_METADATA_KEY}_${username}`;
  }

  static getChats(username: string): Chat[] {
    try {
      const key = this.getChatKey(username);
      const stored = localStorage.getItem(key);
      if (!stored) return [];

      const chats = JSON.parse(stored);
      // Parse dates and validate structure
      return chats.map((chat: any) => ({
        ...chat,
        createdAt: new Date(chat.createdAt),
        updatedAt: new Date(chat.updatedAt),
        messages: chat.messages.map((msg: any) => ({
          ...msg,
          timestamp: new Date(msg.timestamp),
        })),
      })).filter((chat: Chat) => chat && chat.id && chat.messages); // Validate chat structure
    } catch (error) {
      console.error("[CHAT_STORAGE] Error loading chats:", error);
      return [];
    }
  }

  static saveChat(username: string, chat: Chat): void {
    try {
      // Validate chat structure before saving
      if (!chat || !chat.id || !chat.messages) {
        console.error("[CHAT_STORAGE] Invalid chat structure");
        return;
      }

      const chats = this.getChats(username);
      const existingIndex = chats.findIndex((c) => c.id === chat.id);

      if (existingIndex >= 0) {
        chats[existingIndex] = { ...chat, updatedAt: new Date() };
      } else {
        chats.push(chat);
      }

      // Save with metadata
      const key = this.getChatKey(username);
      const metadataKey = this.getMetadataKey(username);
      
      localStorage.setItem(key, JSON.stringify(chats));
      localStorage.setItem(metadataKey, JSON.stringify({
        lastSyncTime: Date.now(),
        version: "1.0",
        totalChats: chats.length
      } as ChatMetadata));
      
      console.log(`[CHAT_STORAGE] Saved chat ${chat.id} for user ${username}`);
    } catch (error) {
      console.error("[CHAT_STORAGE] Error saving chat:", error);
    }
  }

  static deleteChat(username: string, chatId: string): boolean {
    try {
      const chats = this.getChats(username);
      const filteredChats = chats.filter((c) => c.id !== chatId);

      if (filteredChats.length === chats.length) {
        console.warn(`[CHAT_STORAGE] Chat ${chatId} not found for user ${username}`);
        return false;
      }

      const key = this.getChatKey(username);
      const metadataKey = this.getMetadataKey(username);
      
      localStorage.setItem(key, JSON.stringify(filteredChats));
      localStorage.setItem(metadataKey, JSON.stringify({
        lastSyncTime: Date.now(),
        version: "1.0",
        totalChats: filteredChats.length
      } as ChatMetadata));
      
      console.log(`[CHAT_STORAGE] Deleted chat ${chatId} for user ${username}`);
      return true;
    } catch (error) {
      console.error("[CHAT_STORAGE] Error deleting chat:", error);
      return false;
    }
  }

  static createNewChat(username: string, firstMessage?: Message): Chat {
    const now = new Date();
    const chat: Chat = {
      id: `chat_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      title: "New Conversation",
      messages: firstMessage ? [firstMessage] : [],
      createdAt: now,
      updatedAt: now,
      username,
    };

    console.log(`[CHAT_STORAGE] Created new chat ${chat.id} for user ${username}`);
    return chat;
  }

  static updateChatTitle(username: string, chatId: string, title: string): void {
    try {
      const chats = this.getChats(username);
      const chat = chats.find((c) => c.id === chatId);

      if (chat) {
        chat.title = title;
        chat.updatedAt = new Date();
        this.saveChat(username, chat);
        console.log(`[CHAT_STORAGE] Updated chat ${chatId} title to "${title}"`);
      }
    } catch (error) {
      console.error("[CHAT_STORAGE] Error updating chat title:", error);
    }
  }

  static getChat(username: string, chatId: string): Chat | undefined {
    const chats = this.getChats(username);
    return chats.find((c) => c.id === chatId);
  }

  // New method to sync with backend
  static async syncWithBackend(username: string): Promise<boolean> {
    try {
      // In a real implementation, this would sync with the backend
      // For now, we'll just validate the local storage
      const chats = this.getChats(username);
      const metadataKey = this.getMetadataKey(username);
      const metadata = localStorage.getItem(metadataKey);
      
      if (metadata) {
        const parsedMetadata = JSON.parse(metadata) as ChatMetadata;
        console.log(`[CHAT_STORAGE] Sync metadata - Last sync: ${new Date(parsedMetadata.lastSyncTime)}`);
      }
      
      return true;
    } catch (error) {
      console.error("[CHAT_STORAGE] Error syncing with backend:", error);
      return false;
    }
  }

  // New method to export chat history
  static exportChatHistory(username: string): string {
    try {
      const chats = this.getChats(username);
      return JSON.stringify(chats, (key, value) => {
        // Convert Date objects to ISO strings for export
        if (value instanceof Date) {
          return value.toISOString();
        }
        return value;
      }, 2);
    } catch (error) {
      console.error("[CHAT_STORAGE] Error exporting chat history:", error);
      return "";
    }
  }

  // New method to import chat history
  static importChatHistory(username: string, data: string): boolean {
    try {
      const chats = JSON.parse(data);
      if (!Array.isArray(chats)) {
        throw new Error("Invalid chat data format");
      }
      
      // Validate and parse the imported data
      const validatedChats = chats.map((chat: any) => ({
        ...chat,
        createdAt: new Date(chat.createdAt),
        updatedAt: new Date(chat.updatedAt),
        messages: chat.messages.map((msg: any) => ({
          ...msg,
          timestamp: new Date(msg.timestamp),
        })),
      })).filter((chat: Chat) => chat && chat.id && chat.messages);
      
      const key = this.getChatKey(username);
      localStorage.setItem(key, JSON.stringify(validatedChats));
      
      console.log(`[CHAT_STORAGE] Imported ${validatedChats.length} chats for user ${username}`);
      return true;
    } catch (error) {
      console.error("[CHAT_STORAGE] Error importing chat history:", error);
      return false;
    }
  }
}