# OpenManus Lib Directory

Utility functions and shared logic for the OpenManus AI Agent Platform.

## Files

### `chatStorage.ts`
**Purpose**: Manage chat persistence in browser localStorage

**Key Features**:
- Per-user chat isolation (username-based keys)
- CRUD operations for chats and messages
- Automatic timestamp handling
- Type-safe interfaces

**Interfaces**:
```typescript
interface Message {
  id: string;
  type: "user" | "agent" | "tool";
  content: string;
  timestamp: Date;
  toolName?: string;
  quality?: "high" | "medium" | "low";
}

interface Chat {
  id: string;
  title: string;
  messages: Message[];
  createdAt: Date;
  updatedAt: Date;
  username: string;
}
```

**API Methods**:
- `getChats(username)`: Load all chats for a user
- `saveChat(username, chat)`: Save or update a chat
- `deleteChat(username, chatId)`: Remove a chat
- `createNewChat(username, firstMessage?)`: Initialize new chat
- `updateChatTitle(username, chatId, title)`: Update chat title
- `getChat(username, chatId)`: Load single chat

**Storage Keys**:
- Pattern: `openmanus_chats_{username}`
- Example: `openmanus_chats_john_doe`

**Logging**:
- All operations logged with `[CHAT_STORAGE]` prefix
- Helps debugging and tracking data flow

### `utils.ts`
**Purpose**: General utility functions

**Key Function**:
- `cn(...inputs)`: Merge Tailwind classes with clsx and twMerge
  - Handles conditional classes
  - Resolves conflicts
  - Used throughout components

**Usage**:
```typescript
import { cn } from "@/lib/utils";

const className = cn(
  "base-class",
  isActive && "active-class",
  props.className
);
```

## Usage Examples

### Chat Storage
```typescript
import { ChatStorage } from "@/lib/chatStorage";

// Create new chat
const chat = ChatStorage.createNewChat("username");
ChatStorage.saveChat("username", chat);

// Load chats
const chats = ChatStorage.getChats("username");

// Delete chat
ChatStorage.deleteChat("username", chatId);
```

### Class Name Utilities
```typescript
import { cn } from "@/lib/utils";

<div className={cn(
  "base-styles",
  isCollapsed && "collapsed-styles",
  className
)} />
```

## Best Practices

1. **Always validate username** before storage operations
2. **Handle JSON parse errors** gracefully
3. **Log important operations** for debugging
4. **Use type-safe interfaces** for data structures
5. **Clean up expired data** periodically

## Data Flow

```
User Action
    ↓
Component (ChatInterface, Sidebar)
    ↓
ChatStorage API
    ↓
localStorage
    ↓
Browser Cache (persists across sessions)
```

## Future Enhancements

- Migration to IndexedDB for larger datasets
- Cloud sync capabilities
- Encryption for sensitive data
- Offline-first architecture
- Export/import functionality
