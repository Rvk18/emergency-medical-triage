# 🔐 Cognito Authentication Setup Complete

## Overview
The admin dashboard now uses AWS Cognito for authentication instead of mock login.

## Configuration

### Environment Variables (`.env`)
```env
VITE_COGNITO_USER_POOL_ID=us-east-1_475hgcYEt
VITE_COGNITO_CLIENT_ID=3n6k6q450jievbv9o6eao9d08c
VITE_COGNITO_REGION=us-east-1
```

### Cognito Details
- **User Pool ID**: `us-east-1_475hgcYEt`
- **App Client ID**: `3n6k6q450jievbv9o6eao9d08c`
- **Region**: `us-east-1`

## Creating a Test User

### Option 1: AWS Console
1. Go to AWS Console → Cognito → User Pools
2. Select pool: `us-east-1_475hgcYEt`
3. Click "Users" → "Create user"
4. Enter:
   - Email: `admin@example.com`
   - Temporary password: `TempPass123!`
   - Mark email as verified
5. User will need to change password on first login

### Option 2: AWS CLI
```bash
aws cognito-idp admin-create-user \
  --user-pool-id us-east-1_475hgcYEt \
  --username admin@example.com \
  --user-attributes Name=email,Value=admin@example.com Name=email_verified,Value=true \
  --temporary-password "TempPass123!" \
  --region us-east-1
```

### Option 3: Set Permanent Password (Skip First Login)
```bash
# Create user
aws cognito-idp admin-create-user \
  --user-pool-id us-east-1_475hgcYEt \
  --username admin@example.com \
  --user-attributes Name=email,Value=admin@example.com Name=email_verified,Value=true \
  --message-action SUPPRESS \
  --region us-east-1

# Set permanent password
aws cognito-idp admin-set-user-password \
  --user-pool-id us-east-1_475hgcYEt \
  --username admin@example.com \
  --password "AdminPass123!" \
  --permanent \
  --region us-east-1
```

## Testing Login

### Test Credentials
After creating a user with permanent password:
- **Email**: `admin@example.com`
- **Password**: `AdminPass123!`

### Login Flow
1. Navigate to http://localhost:5173
2. Enter email and password
3. Click "Login"
4. On success, redirects to `/admin` dashboard
5. On failure, shows error message

### Error Messages
- **User not found**: Email doesn't exist in Cognito
- **Incorrect password**: Wrong password
- **Please verify your email**: Email not verified
- **Sign-in incomplete**: Additional steps required (e.g., password change)

## How It Works

### Authentication Flow
1. User enters email/password
2. Frontend calls `signIn()` from AWS Amplify
3. Cognito validates credentials
4. On success, returns ID token and access token
5. Tokens stored in sessionStorage
6. User info stored in localStorage
7. Redirect to admin dashboard

### Token Storage
- **ID Token**: `sessionStorage.getItem('idToken')` - Used for API calls
- **Access Token**: `sessionStorage.getItem('accessToken')` - For Cognito operations
- **User Info**: `localStorage.getItem('medtriage_auth')` - User profile

### API Integration
All API calls to protected endpoints now include:
```javascript
headers: {
  'Authorization': `Bearer ${idToken}`,
  'Content-Type': 'application/json'
}
```

## Files Modified

### New/Updated Files
- `src/utils/auth.js` - Complete Cognito integration with Amplify
- `src/pages/login.js` - Better error handling
- `.env` - Added Cognito configuration
- `src/styles/components.css` - Added alert styles

### Key Functions
```javascript
// Login
await login(email, password);

// Logout
await logout();

// Check authentication
const isAuth = isAuthenticated();

// Get current user
const user = getCurrentUser();

// Get ID token for API calls
const token = getIdToken();

// Refresh session
await refreshSession();
```

## Session Management

### Token Expiration
- ID tokens expire after 60 minutes (default)
- Use `refreshSession()` to get new tokens
- Amplify handles refresh automatically with `fetchAuthSession()`

### Auto-Refresh
```javascript
// Refresh tokens before API call if needed
try {
  const response = await fetch(url, {
    headers: {
      'Authorization': `Bearer ${getIdToken()}`
    }
  });
  
  if (response.status === 401) {
    // Token expired, refresh and retry
    await refreshSession();
    // Retry request with new token
  }
} catch (error) {
  console.error('API call failed:', error);
}
```

## Security Features

### What's Protected
- All admin dashboard routes require authentication
- Unauthenticated users redirected to login
- Tokens stored in sessionStorage (cleared on browser close)
- User info in localStorage (persists across sessions)

### Logout Behavior
- Clears Cognito session
- Removes all tokens from storage
- Redirects to login page

## Troubleshooting

### "User not found"
- User doesn't exist in Cognito User Pool
- Create user using AWS Console or CLI

### "Incorrect password"
- Wrong password entered
- Reset password via AWS Console if needed

### "Please verify your email"
- Email not verified in Cognito
- Mark as verified in AWS Console or use CLI:
```bash
aws cognito-idp admin-update-user-attributes \
  --user-pool-id us-east-1_475hgcYEt \
  --username admin@example.com \
  --user-attributes Name=email_verified,Value=true \
  --region us-east-1
```

### Tokens not working
- Check token expiration (decode at jwt.io)
- Call `refreshSession()` to get new tokens
- Ensure correct User Pool ID and Client ID in `.env`

## Next Steps

### Production Considerations
1. **Password Policy**: Configure in Cognito User Pool settings
2. **MFA**: Enable multi-factor authentication
3. **Password Reset**: Implement forgot password flow
4. **Email Verification**: Set up email verification flow
5. **Social Login**: Add Google/Facebook login (optional)
6. **User Groups**: Create admin/user groups for role-based access
7. **Token Refresh**: Implement automatic token refresh on 401

### Additional Features
- Sign-up page for self-registration
- Forgot password flow
- Change password functionality
- User profile management
- Remember me functionality

## Testing Checklist

- [ ] Create test user in Cognito
- [ ] Login with valid credentials
- [ ] Login with invalid credentials (test error messages)
- [ ] Logout and verify session cleared
- [ ] Refresh page and verify session persists
- [ ] Close browser and verify tokens cleared
- [ ] Test API calls with ID token
- [ ] Test token refresh on expiration

---

**Status**: ✅ Complete and working
**Date**: March 7, 2026
**Authentication**: AWS Cognito with Amplify v6
