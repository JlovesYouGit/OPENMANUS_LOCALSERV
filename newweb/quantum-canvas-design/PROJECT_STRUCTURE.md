# OpenManus Project Structure

Complete overview of the OpenManus AI Agent Platform architecture.

## Directory Structure

```
openmanus/
├── public/                      # Static assets
│   ├── robots.txt              # SEO robots file
│   └── favicon.ico             # Site icon
│
├── src/                         # Source code
│   ├── components/             # Reusable UI components
│   │   ├── ui/                # Shadcn UI components
│   │   ├── AnimatedBackground.tsx
│   │   ├── ChatbotAvatar.tsx
│   │   ├── ChatInterface.tsx
│   │   ├── Header.tsx
│   │   ├── Sidebar.tsx
│   │   └── README.md
│   │
│   ├── contexts/              # React Context providers
│   │   ├── AuthContext.tsx
│   │   └── README.md
│   │
│   ├── hooks/                 # Custom React hooks
│   │   ├── use-mobile.tsx
│   │   └── use-toast.ts
│   │
│   ├── lib/                   # Utility functions
│   │   ├── chatStorage.ts
│   │   ├── utils.ts
│   │   └── README.md
│   │
│   ├── pages/                 # Route components
│   │   ├── Index.tsx
│   │   ├── Login.tsx
│   │   ├── NotFound.tsx
│   │   └── README.md
│   │
│   ├── App.css               # Legacy styles (unused)
│   ├── App.tsx               # Root component
│   ├── index.css             # Global styles & design system
│   ├── main.tsx              # Application entry point
│   └── vite-env.d.ts         # TypeScript definitions
│
├── index.html                 # HTML entry point
├── tailwind.config.ts         # Tailwind CSS configuration
├── vite.config.ts            # Vite build configuration
├── tsconfig.json             # TypeScript configuration
├── package.json              # Dependencies
└── README.md                 # Project documentation
```

## Architecture Overview

### Application Flow

```
main.tsx
    ↓
App.tsx (QueryClient + Router)
    ↓
AuthProvider (global auth state)
    ↓
Routes
    ├── /login → Login.tsx (public)
    └── / → Index.tsx (protected)
            ├── Header
            ├── Sidebar (chat list)
            └── ChatInterface
```

### State Management

1. **Global State** (Context API)
   - AuthContext: User authentication
   - Location: `src/contexts/`

2. **Local State** (useState)
   - Component-level state
   - Form inputs, UI toggles

3. **Persistent State** (localStorage)
   - User sessions (24h)
   - Chat history per user
   - Managed by ChatStorage

### Data Flow

```
User Input
    ↓
Component Handler
    ↓
ChatStorage API
    ↓
localStorage (browser)
    ↓
Context Update
    ↓
Components Re-render
```

## Technology Stack

### Core
- **React 18.3.1**: UI library
- **TypeScript**: Type safety
- **Vite**: Build tool & dev server
- **React Router 6**: Routing

### Styling
- **Tailwind CSS**: Utility-first CSS
- **shadcn/ui**: Component library
- **Radix UI**: Accessible primitives
- **Lucide React**: Icon system

### State & Data
- **React Context**: Global state
- **localStorage**: Data persistence
- **TanStack Query**: API state (ready for backend)
- **Zod**: Schema validation

### UI Components
- **Sonner**: Toast notifications
- **Radix Primitives**: Accessible components
- **CVA**: Component variants

## Design System

Location: `src/index.css`

### Color Tokens
```css
--background: Dark base (HSL)
--foreground: Light text
--primary: Cyan/teal accent
--secondary: Purple accent
--muted: Subdued elements
--border: Component borders
--destructive: Error states
```

### Custom Utilities
- `.glass`: Glassmorphism effect
- `.glow-primary`: Primary color glow
- `.gradient-text`: Gradient text fill
- `.hover-scale`: Scale on hover
- `.hover-lift`: Lift on hover

### Animations
- `fadeInUp`: Entrance animation
- `slideInRight`: Slide entrance
- `pulseGlow`: Pulsing glow effect
- `shimmer`: Loading shimmer

## Component Patterns

### Compound Components
```typescript
<Sidebar
  collapsed={collapsed}
  onToggle={handleToggle}
  currentChatId={chatId}
  onChatSelect={handleSelect}
/>
```

### Render Props
```typescript
{chats.map((chat) => (
  <ChatItem key={chat.id} {...chat} />
))}
```

### Custom Hooks
```typescript
const { username, login, logout } = useAuth();
const isMobile = useIsMobile();
const { toast } = useToast();
```

## Authentication Flow

1. User visits `/`
2. Check `isAuthenticated` in AuthContext
3. If false → redirect to `/login`
4. Login with username (2-20 chars)
5. Validate with Zod schema
6. Save to localStorage (24h expiry)
7. Redirect to `/`
8. Load user's chat history

## Chat System Flow

1. User logs in → Load chats from storage
2. Select chat or create new
3. Type message → Save to localStorage
4. Simulate agent response
5. Update chat title from first message
6. Display with animated avatar states
7. Delete chat → Confirm → Remove from storage

## API Endpoints (Future)

Ready to integrate with backend:

```
POST   /api/auth/login
POST   /api/auth/logout
GET    /api/chats
POST   /api/chats
GET    /api/chats/:id
DELETE /api/chats/:id
POST   /api/messages
GET    /api/messages/:chatId
```

## Build & Deployment

### Development
```bash
npm run dev      # Start dev server (port 8080)
npm run build    # Production build
npm run preview  # Preview production build
```

### Production
- Build output: `dist/`
- Assets optimization: Automatic
- Code splitting: Enabled
- Tree shaking: Enabled

### Environment Variables
Currently using client-side only. For backend:
```
VITE_API_URL=https://api.example.com
VITE_WS_URL=wss://ws.example.com
```

## Performance Optimizations

1. **Code Splitting**: Routes lazy-loaded
2. **Tree Shaking**: Unused code removed
3. **Asset Optimization**: Images compressed
4. **Lazy Loading**: Components loaded on demand
5. **Memoization**: Expensive computations cached

## Security Considerations

### Current
- Client-side validation (Zod)
- Input sanitization
- XSS prevention (React escaping)
- localStorage encryption (future)

### Future
- Backend authentication
- JWT tokens
- Rate limiting
- CSRF protection
- Content Security Policy

## Testing Strategy

### Unit Tests
- Components: React Testing Library
- Utilities: Jest
- Hooks: React Hooks Testing Library

### Integration Tests
- User flows: Cypress
- API mocking: MSW

### E2E Tests
- Full flows: Playwright
- Cross-browser: BrowserStack

## Logging & Debugging

Console log prefixes:
- `[AUTH]`: Authentication events
- `[CHAT]`: Chat operations
- `[CHAT_STORAGE]`: Storage operations

Example:
```
[AUTH] User logged in: john_doe at 2025-01-15T10:30:00Z
[CHAT] Created new chat chat_1705315800000_abc123
[CHAT_STORAGE] Saved chat chat_1705315800000_abc123 for user john_doe
```

## Browser Support

- Chrome/Edge: 90+
- Firefox: 88+
- Safari: 14+
- Mobile: iOS 14+, Android 10+

## Accessibility

- ARIA labels on interactive elements
- Keyboard navigation support
- Screen reader compatible
- Focus management
- Color contrast WCAG AA compliant

## License

OpenManus AI Agent Platform
