# OpenManus Cover Page Deployment Guide

## Overview
This guide explains how to deploy the OpenManus cover page with login functionality while preserving the original Figma design.

## Prerequisites
- Node.js (v14 or higher)
- npm (v6 or higher)

## Directory Structure
```
OpenManus/
└── coverpage/
    ├── Animatedlandingpagedesign/          # Main development directory
    │   ├── src/
    │   │   └── components/
    │   │       ├── LandingPage.tsx         # Modified with login functionality
    │   │       └── Navigation.tsx          # Original design preserved
    │   ├── dist/                           # Built files
    │   │   └── index.html                  # Static HTML version (fallback)
    │   ├── package.json
    │   └── vite.config.ts
    └── Animatedlandingpagedesign-main/     # Original Figma design reference
```

## Deployment Options

### Option 1: Using the Static HTML Version (Recommended for Quick Deployment)
The `dist/index.html` file is a standalone HTML file that includes all necessary CSS and JavaScript. This version:
- Preserves all visual design elements
- Includes login functionality
- Works without any build tools
- Can be served directly by any web server

To deploy:
1. Copy `dist/index.html` to your web server's root directory
2. Ensure your server is configured to serve the file at the root path (/)
3. The login functionality will automatically redirect to /app after successful authentication

### Option 2: Building from Source (For Development/Customization)
If you need to modify the cover page or integrate it into a larger application:

1. Navigate to the development directory:
   ```
   cd Animatedlandingpagedesign
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Build the project:
   ```
   npm run build
   ```

4. The built files will be in the `dist/` directory

## Login Functionality

### How It Works
1. User clicks "Access Chat" or "Start Building Now" button
2. A modal login form appears
3. User enters a username (2-20 characters: letters, numbers, underscores, hyphens)
4. Upon successful validation:
   - Username is stored in localStorage
   - User is redirected to `/app`
5. The main OpenManus application reads the username from localStorage

### Integration with Main Application
The login system is designed to work seamlessly with the existing OpenManus application:
- Uses the same localStorage keys (`openmanus_username`, `openmanus_last_login`, `openmanus_session_id`)
- Redirects to the same endpoint (`/app`)
- Maintains consistent user experience

## Customization

### Changing Redirect URL
To change where users are redirected after login:
1. Open `src/components/LandingPage.tsx`
2. Find the line: `window.location.href = '/app';`
3. Change `/app` to your desired path

### Modifying Validation Rules
To change username validation rules:
1. Open `src/components/LandingPage.tsx`
2. Find the `usernameRegex` variable
3. Modify the regular expression as needed
4. Update the error message accordingly

## Troubleshooting

### Build Issues
If you encounter build errors:
1. Delete `node_modules` directory
2. Delete `package-lock.json`
3. Run `npm install`
4. Run `npm run build`

### Runtime Issues
If the login functionality doesn't work:
1. Ensure localStorage is available in the browser
2. Check browser console for JavaScript errors
3. Verify that the redirect URL (`/app`) is correct

## Fallback Solution
If the React/TypeScript version cannot be built:
1. Use the static HTML version in `dist/index.html`
2. This version contains all functionality and design elements
3. No build process required

## Testing
Run the validation tests:
```
node test_login_functionality.js
```

This will verify that the username validation logic works correctly.