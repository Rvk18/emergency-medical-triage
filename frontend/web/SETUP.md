# Setup Instructions

## Phase 1: Foundation - COMPLETE ✅

The foundation has been set up with:
- ✅ Design system (tokens, global styles, components)
- ✅ Theme system (light/dark mode)
- ✅ Hash-based SPA router
- ✅ Session management
- ✅ App shell (topbar, navigation, content area)
- ✅ Offline detection banner
- ✅ Placeholder pages for all routes

## Quick Start

### Prerequisites

If you don't have Node.js installed:

```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Add Homebrew to PATH (for zsh)
echo 'eval "$(/opt/homebrew/bin/brew shellenv zsh)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv zsh)"

# Install Node.js (v18+)
brew install node

# Verify installation
node --version  # Should show v18 or higher
npm --version
```

### Setup & Run

```bash
# 1. Install dependencies
npm install

# 2. Copy environment variables
cp .env.example .env

# 3. Start development server
npm run dev

# 4. Open http://localhost:5173
```

## What's Working

- ✅ Light/Dark theme toggle
- ✅ Navigation between pages
- ✅ Offline detection
- ✅ Session management (UUID generation)
- ✅ Responsive design
- ✅ Login page (mock auth)
- ✅ Placeholder pages for all routes

## Next Steps

### Phase 2: Auth & Language (1-2 days)
- [ ] Implement real auth with JWT
- [ ] Add language selector (7 languages)
- [ ] Create translation system
- [ ] Add role-based access control

### Phase 3: Core Triage Flow (3-4 days)
- [ ] Build 4-step triage wizard
- [ ] Integrate with POST /triage API
- [ ] Add form validation
- [ ] Implement safety guardrails
- [ ] Create triage report view

### Phase 4: Hospital Matching & Routing (2-3 days)
- [ ] Build hospital match screen
- [ ] Integrate with POST /hospitals API
- [ ] Add navigation/routing UI
- [ ] Create handoff report generator

### Phase 5: RMP Features (2-3 days)
- [ ] Build RMP dashboard
- [ ] Add guidance overlay
- [ ] Create learning modules screen

### Phase 6: Admin & Hospital Staff (2-3 days)
- [ ] Build admin dashboard
- [ ] Create hospital staff portal
- [ ] Add analytics views

## Testing

```bash
# Test the app
npm run dev

# Navigate to different pages:
# - http://localhost:5173/#/
# - http://localhost:5173/#/triage
# - http://localhost:5173/#/hospitals
# - http://localhost:5173/#/dashboard
# - http://localhost:5173/#/admin

# Test theme toggle (moon icon in top right)
# Test offline mode (disable network in DevTools)
```

## Verification Checklist

- [ ] App loads without errors
- [ ] Theme toggle works (light ↔ dark)
- [ ] Navigation works (all links)
- [ ] Offline banner shows when offline
- [ ] Responsive on mobile (375px width)
- [ ] All placeholder pages render

## Troubleshooting

**Port already in use?**
```bash
# Kill process on port 5173
lsof -ti:5173 | xargs kill -9
```

**Dependencies not installing?**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

**Styles not loading?**
```bash
# Restart dev server
npm run dev
```

## Architecture

```
src/
├── main.js              # App entry point
├── style.css            # Import all styles
├── styles/              # Design system
│   ├── tokens.css      # Design tokens
│   ├── global.css      # Base styles
│   └── components.css  # Component styles
├── utils/               # Utilities
│   ├── theme.js        # Theme management
│   ├── router.js       # SPA router
│   └── session.js      # Session management
└── pages/               # Route pages
    ├── login.js
    ├── triage-wizard.js
    ├── hospital-match.js
    ├── rmp-dashboard.js
    └── admin-dashboard.js
```

## Ready for Phase 2!

The foundation is complete. You can now start implementing Phase 2 (Auth & Language) or Phase 3 (Triage Flow).
