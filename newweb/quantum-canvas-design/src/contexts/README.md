# OpenManus Contexts Directory

React Context providers for global state management.

## AuthContext.tsx

**Purpose**: Manage user authentication state across the application

### Features

1. **Username-based Authentication**
   - Simple, no-password login system
   - 2-20 character username validation
   - Alphanumeric + underscores/hyphens only

2. **Session Management**
   - 24-hour auto-login from localStorage
   - Automatic session expiration
   - Console logging for debugging

3. **Validation**
   - Zod schema validation
   - User-friendly error messages
   - Sanitized input handling

### API

#### Context Value
```typescript
interface AuthContextType {
  username: string | null;
  login: (username: string) => Promise<{ success: boolean; error?: string }>;
  logout: () => void;
  isAuthenticated: boolean;
}
```

#### Storage Keys
- `openmanus_username`: Current username
- `openmanus_last_login`: ISO timestamp of login

### Usage

```typescript
import { useAuth } from "@/contexts/AuthContext";

function MyComponent() {
  const { username, login, logout, isAuthenticated } = useAuth();

  const handleLogin = async () => {
    const result = await login("myusername");
    if (result.success) {
      // Navigate to dashboard
    } else {
      // Show error: result.error
    }
  };

  return (
    <div>
      {isAuthenticated ? (
        <p>Welcome, {username}!</p>
      ) : (
        <button onClick={handleLogin}>Login</button>
      )}
    </div>
  );
}
```

### Security Considerations

**Current Implementation**:
- Username-only authentication (no passwords)
- Client-side validation only
- localStorage persistence

**For Production**:
- Add backend authentication
- Implement JWT tokens
- Add password requirements
- Enable 2FA options
- Use secure httpOnly cookies
- Add rate limiting

### Logging

All authentication events logged with `[AUTH]` prefix:
- Login: `[AUTH] User logged in: {username} at {timestamp}`
- Logout: `[AUTH] User logged out`
- Auto-login: `[AUTH] Auto-logged in as: {username}`
- Expired: `[AUTH] Session expired, cleared cache`

### Session Flow

```
User enters username
    ↓
Zod validation
    ↓
Save to localStorage
    ↓
Update context state
    ↓
Components re-render
    ↓
Auto-check on page load (< 24 hours)
```

### Error Handling

```typescript
try {
  const result = await login(username);
  if (!result.success) {
    // Handle validation errors
    toast.error(result.error);
  }
} catch (error) {
  // Handle unexpected errors
  toast.error("Login failed. Please try again.");
}
```

## Provider Setup

In `App.tsx`:
```typescript
import { AuthProvider } from "@/contexts/AuthContext";

<AuthProvider>
  <Routes>
    <Route path="/login" element={<Login />} />
    <Route path="/" element={<Index />} />
  </Routes>
</AuthProvider>
```

## Future Enhancements

- OAuth integration (Google, GitHub)
- Multi-factor authentication
- Role-based access control
- Session timeout warnings
- Remember me checkbox
- Password reset flow
