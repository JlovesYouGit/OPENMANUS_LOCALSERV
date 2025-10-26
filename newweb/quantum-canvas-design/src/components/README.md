# OpenManus Components Directory

This directory contains all reusable UI components for the OpenManus AI Agent Platform.

## Component Structure

### Core Components

#### `AnimatedBackground.tsx`
- Renders animated background effects with gradient orbs, grid, and floating particles
- Used across login and main application pages
- Provides immersive futuristic atmosphere

#### `ChatbotAvatar.tsx`
- Dynamic avatar component with three states:
  - `idle`: Sparkles icon (default state)
  - `processing`: Hand icon with bounce animation (thinking)
  - `responding`: Smile icon (actively replying)
- Includes shimmer effect and glow animations

#### `ChatInterface.tsx`
- Main chat interface with message bubbles
- Features:
  - User/Agent/Tool message types
  - Quality indicators (high/medium/low)
  - Tool usage badges
  - Real-time typing indicators
  - Auto-save to localStorage
  - Message timestamps

#### `Header.tsx`
- Application header with:
  - OpenManus branding
  - Connection status indicator
  - Authentication buttons
  - Responsive design

#### `Sidebar.tsx`
- Navigation sidebar with:
  - Chat history list
  - New chat button
  - Delete chat functionality
  - User profile display
  - Logout button
  - Collapsible design

### UI Components (`ui/` directory)
Shadcn UI components - pre-built, accessible components following Radix UI principles.

## Usage Guidelines

### Importing Components
```typescript
import { ChatInterface } from "@/components/ChatInterface";
import { AnimatedBackground } from "@/components/AnimatedBackground";
import { ChatbotAvatar } from "@/components/ChatbotAvatar";
```

### State Management
Components use:
- **AuthContext**: Username authentication and session management
- **ChatStorage**: Browser localStorage for chat persistence
- **React Hooks**: useState, useEffect for local state

### Styling
- All components use Tailwind CSS with semantic tokens
- Design system defined in `src/index.css`
- Glass morphism effects via `.glass` utility class
- Gradient and glow effects via CSS custom properties

## Component Dependencies

```
App.tsx
├── AuthProvider (context)
├── pages/
│   ├── Login.tsx
│   │   └── AnimatedBackground
│   └── Index.tsx
│       ├── AnimatedBackground
│       ├── Header
│       ├── Sidebar
│       └── ChatInterface
│           └── ChatbotAvatar
```

## Adding New Components

1. Create component file in this directory
2. Use TypeScript for type safety
3. Follow existing naming conventions (PascalCase)
4. Export as named export
5. Add to this README
6. Use semantic tokens from design system

## Testing Components

When pushing to project directory, verify:
- All imports resolve correctly
- Props are properly typed
- Responsive design works on mobile/desktop
- Animations perform smoothly
- LocalStorage persists correctly
- Authentication flows work end-to-end
