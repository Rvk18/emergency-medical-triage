# Admin Dashboard - Quick Start Guide

**Last Updated:** March 7, 2026  
**Purpose:** Get the admin dashboard up and running quickly

---

## Prerequisites

1. **Node.js 18+** installed
2. **Google Maps API key** (see [GOOGLE-MAPS-ACCOUNT-SETUP.md](../infrastructure/GOOGLE-MAPS-ACCOUNT-SETUP.md))
3. **AWS Cognito credentials** (User Pool ID, Client ID from backend team)
4. **Backend API URL** (from Terraform outputs)

---

## Setup Steps

### 1. Install Dependencies

```bash
cd emergency-medical-triage/frontend/web
npm install
```

### 2. Configure Environment Variables

Copy the example file and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env`:

```bash
# Backend API
VITE_API_URL=https://vrxlwtzfff.execute-api.us-east-1.amazonaws.com/dev

# AWS Cognito (from backend team)
VITE_COGNITO_USER_POOL_ID=us-east-1_xxxxxxxxx
VITE_COGNITO_CLIENT_ID=xxxxxxxxxxxxxxxxxxxxxxxxxx
VITE_COGNITO_REGION=us-east-1

# Google Maps
VITE_GOOGLE_MAPS_API_KEY=AIza...your_key_here
```

### 3. Start Development Server

```bash
npm run dev
```

Open http://localhost:5173 in your browser.

---

## First Time Login

### Create Admin User in Cognito

If you don't have an admin user yet, create one using AWS CLI:

```bash
aws cognito-idp admin-create-user \
  --user-pool-id us-east-1_xxxxxxxxx \
  --username admin@example.com \
  --user-attributes Name=email,Value=admin@example.com Name=email_verified,Value=true \
  --temporary-password "TempPass123!"
```

Or use the AWS Console:
1. Go to Cognito → User Pools → your pool
2. Click "Users" → "Create user"
3. Enter email and temporary password
4. User will be prompted to change password on first login

### Login to Dashboard

1. Navigate to http://localhost:5173
2. Enter your admin email and password
3. If using temporary password, you'll be prompted to set a new one
4. After successful login, you'll see the admin dashboard

---

## Dashboard Overview

### Main Sections

1. **Top Bar**
   - System status indicator
   - Alert notifications
   - Admin profile dropdown

2. **Map View** (center-left)
   - Patient markers (color-coded by severity)
   - Hospital markers (with capacity badges)
   - Route polylines
   - Click markers for details

3. **Patient List** (right panel)
   - Active patients in transit
   - Severity, ETA, destination
   - Click to view details or re-route

4. **Hospital Status** (bottom)
   - All hospitals with capacity
   - Incoming patient counts
   - Availability status

---

## Common Tasks

### Monitor Active Patients

1. View the patient list on the right
2. Patients are sorted by severity (Critical first)
3. Each card shows:
   - Patient ID/name
   - Severity level
   - Current ETA
   - Destination hospital

### Track Patient Location

1. Find the patient in the list
2. Click on their card
3. The map will center on their location
4. The route to their destination is highlighted

### Re-route a Patient

1. Click on a patient card
2. Click "Re-route" button in the detail modal
3. View alternative hospital recommendations
4. Select new hospital
5. Review new route and ETA
6. Confirm re-routing
7. System notifies the RMP/ambulance

### Check Hospital Capacity

1. View the hospital status panel at the bottom
2. Green = Available, Yellow = Limited, Red = Full
3. Click on a hospital for detailed capacity by department
4. See incoming patient count

---

## Real-time Updates

The dashboard automatically updates every 5 seconds:
- Patient locations
- ETAs
- Hospital capacity
- System alerts

You'll see a subtle indicator when data is refreshing.

---

## Troubleshooting

### Map Not Loading

**Problem:** Blank map or "For development purposes only" watermark

**Solution:**
1. Check your Google Maps API key in `.env`
2. Ensure Maps JavaScript API is enabled in Google Cloud Console
3. Check browser console for API errors
4. Verify billing is enabled on your Google Cloud project

### Authentication Errors

**Problem:** "Invalid credentials" or "User not found"

**Solution:**
1. Verify Cognito User Pool ID and Client ID in `.env`
2. Check that user exists in Cognito User Pool
3. Ensure user's email is verified
4. Try resetting password in AWS Console

### No Patients Showing

**Problem:** Patient list is empty

**Solution:**
1. Check that backend API is running
2. Verify API URL in `.env`
3. Check browser console for API errors
4. Ensure there are active patients in the system (test with mobile app)
5. Check network tab for failed API calls

### Re-routing Not Working

**Problem:** Re-route button doesn't work or fails

**Solution:**
1. Check that POST /admin/patients/{id}/reroute endpoint exists
2. Verify admin has permission to re-route
3. Check browser console for errors
4. Ensure alternative hospitals are available

---

## Development Tips

### Mock Data for Testing

If backend is not ready, use mock data:

```javascript
// src/data/mock-admin.js
export const mockPatients = [
  {
    id: "patient-1",
    patient_name: "Test Patient",
    severity: "critical",
    current_location: { lat: 12.97, lon: 77.59 },
    destination_hospital_id: "hospital-1",
    destination_hospital_name: "Apollo Hospital",
    eta_minutes: 12,
    distance_remaining_km: 8.5,
    status: "en_route"
  }
];
```

Enable mock mode in `src/services/admin-api.js`:

```javascript
const USE_MOCK_DATA = import.meta.env.VITE_USE_MOCK === 'true';
```

### Hot Reload

Vite provides instant hot reload. Changes to:
- JavaScript files → instant update
- CSS files → instant update
- HTML → page refresh

### Browser DevTools

Useful panels:
- **Console:** Check for errors and API responses
- **Network:** Monitor API calls and responses
- **Application → Local Storage:** View stored auth tokens
- **Application → Session Storage:** View session data

---

## Next Steps

1. **Read the refactor plan:** [ADMIN-DASHBOARD-REFACTOR.md](./ADMIN-DASHBOARD-REFACTOR.md)
2. **Review API integration:** [API-Integration-Guide.md](./API-Integration-Guide.md)
3. **Understand authentication:** [RMP-AUTH.md](./RMP-AUTH.md)
4. **Start implementing:** Follow the 6-day implementation plan

---

## Support

- Check documentation in `docs/frontend/`
- Review backend API docs in `docs/backend/`
- Test API endpoints with curl (see [TESTING-Pipeline-curl.md](../backend/TESTING-Pipeline-curl.md))
- Check CloudWatch logs for backend errors

---

## Production Deployment

When ready to deploy:

1. Build production bundle:
   ```bash
   npm run build
   ```

2. Preview production build:
   ```bash
   npm run preview
   ```

3. Deploy `dist/` folder to:
   - AWS S3 + CloudFront
   - Vercel
   - Netlify
   - Any static hosting

4. Update environment variables for production:
   - Use production API URL
   - Use production Cognito pool
   - Restrict Google Maps API key to production domain

---

**You're ready to start building the admin dashboard!**
