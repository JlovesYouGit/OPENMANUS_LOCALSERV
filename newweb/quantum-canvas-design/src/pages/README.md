# OpenManus Pages Directory

Top-level route components for the OpenManus AI Agent Platform.

## Page Structure

### Index.tsx
**Route**: `/`  
**Purpose**: Main application dashboard with chat interface

**Features**:
- Protected route (requires authentication)
- Chat management (create, select, delete)
- Sidebar with chat history
- Real-time message interface
- Animated background effects

**State Management**:
- `currentChatId`: Active chat session
- `sidebarCollapsed`: Sidebar visibility
- `refreshTrigger`: Force chat list updates

**Lifecycle**:
1. Check authentication → redirect to `/login` if needed
2. Load existing chats or create new one
3. Render chat interface with selected chat
4. Handle chat operations (new, select, delete)

**Component Tree**:
```
Index
├── AnimatedBackground
├── Header
├── Sidebar
│   └── Chat list with delete
└── ChatInterface
    └── ChatbotAvatar (dynamic states)
```

### Login.tsx
**Route**: `/login`  
**Purpose**: User authentication page

**Features**:
- Username input with validation (2-20 chars)
- Real-time validation feedback
- Auto-redirect if already authenticated
- Loading states during login
- Session persistence info

**Form Validation**:
- Client-side: Zod schema
- Pattern: alphanumeric + underscores/hyphens
- Max length: 20 characters
- Min length: 2 characters

**User Flow**:
1. User enters username
2. Validation checks (instant feedback)
3. Submit → AuthContext.login()
4. Success → Navigate to `/`
5. Error → Display toast message

**UI Elements**:
- Glassmorphism login card
- Animated logo with gradient
- Accessibility-focused inputs
- Session duration notice

### NotFound.tsx
**Route**: `*` (catch-all)  
**Purpose**: 404 error page

**Features**:
- Logged to console for debugging
- User-friendly error message
- Link back to homepage
- Clean, minimal design

**Console Logging**:
```
404 Error: User attempted to access non-existent route: /invalid-path
```

## Routing Configuration

In `App.tsx`:
```typescript
<Routes>
  <Route path="/" element={<Index />} />
  <Route path="/login" element={<Login />} />
  <Route path="*" element={<NotFound />} />
</Routes>
```

## Protected Routes

Pages that require authentication:
- `/` (Index) - Checks `isAuthenticated` and redirects

Public routes:
- `/login` - Auto-redirects if authenticated
- `/404` - Always accessible

## Navigation Patterns

### Programmatic Navigation
```typescript
import { useNavigate } from "react-router-dom";

const navigate = useNavigate();
navigate("/"); // Go to dashboard
navigate("/login"); // Go to login
```

### Link Components
```typescript
import { Link } from "react-router-dom";

<Link to="/login">Sign In</Link>
```

## Page Layout Standards

All pages follow this structure:
```typescript
const PageName = () => {
  // 1. Hooks (auth, navigation, state)
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();
  
  // 2. Effects (redirects, data loading)
  useEffect(() => {
    if (!isAuthenticated) {
      navigate("/login");
    }
  }, [isAuthenticated, navigate]);
  
  // 3. Handlers (user actions)
  const handleAction = () => {
    // Logic here
  };
  
  // 4. Early returns (loading, errors)
  if (loading) return <LoadingSpinner />;
  
  // 5. Main render
  return (
    <div className="page-container">
      {/* Page content */}
    </div>
  );
};
```

## SEO Optimization

Each page should include:
- Semantic HTML (`<main>`, `<header>`, `<section>`)
- Proper heading hierarchy (single `<h1>`)
- Meta descriptions (via Helmet if added)
- Alt text for images
- Accessible form labels

## Performance Considerations

- Lazy load routes with React.lazy()
- Code splitting for large pages
- Optimize images and animations
- Minimize re-renders with memo/useMemo
- Use React.Suspense for async loading

## Testing Pages

When testing routes:
1. Verify authentication redirects work
2. Check protected route access
3. Test navigation flows
4. Validate form submissions
5. Confirm error handling
6. Check mobile responsiveness

## Adding New Pages

1. Create component in `src/pages/`
2. Add route to `App.tsx`
3. Update navigation links
4. Add to this README
5. Test all user flows
6. Verify authentication if protected
