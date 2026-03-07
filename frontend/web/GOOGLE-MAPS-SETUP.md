# Google Maps Setup Guide

## Architecture

The Google Maps API key is securely stored in **AWS Secrets Manager** and fetched by the frontend through a backend API endpoint.

```
AWS Secrets Manager
       ↓
Backend Lambda (/config endpoint)
       ↓
Frontend (fetches key via API)
       ↓
Google Maps JavaScript API
```

**Why this is secure:**
- API key never stored in frontend code or .env files
- Backend controls access to the secret
- Key is fetched dynamically at runtime
- Standard practice for sensitive configuration

---

## Setup Steps

### 1. Deploy Backend Infrastructure

The `/config` endpoint needs to be deployed first:

```bash
cd infrastructure

# Make sure Google Maps API key is in terraform.tfvars
# google_maps_api_key = "AIza...your_key"

# Deploy
terraform apply
```

This creates:
- Lambda function for `/config` endpoint
- API Gateway route `GET /config`
- Permissions to read from Secrets Manager

### 2. Test the Config Endpoint

```bash
# Get API URL
API_URL=$(terraform output -raw api_gateway_url)

# Test config endpoint
curl -s "${API_URL}/config" | jq
```

Expected response:
```json
{
  "google_maps_api_key": "AIza...your_key",
  "environment": "dev"
}
```

### 3. Start Frontend

```bash
cd ../frontend/web

# No .env changes needed!
# The frontend will fetch the key from the backend

npm run dev
```

### 4. Verify Map Loads

1. Open http://localhost:5173
2. Login (any credentials work with mock auth)
3. Go to Dashboard tab
4. Map should load with patient and hospital markers

---

## How It Works

### Backend (`/config` endpoint)

```python
# infrastructure/config_lambda_src/lambda_handler.py
def handler(event, context):
    # Fetch from Secrets Manager using boto3
    api_key = get_secret("google-maps-config")
    return {"google_maps_api_key": api_key}
```

### Frontend

```javascript
// src/services/config.js
export async function getGoogleMapsApiKey() {
  const response = await fetch(`${API_URL}/config`);
  const config = await response.json();
  return config.google_maps_api_key;
}

// src/utils/google-maps.js
export async function loadGoogleMaps() {
  const apiKey = await getGoogleMapsApiKey(); // Fetch from backend
  // Load Google Maps script with the key
}
```

---

### 4. Test the Map

1. Open http://localhost:5173
2. Login (any credentials work with mock auth)
3. Go to Dashboard tab
4. You should see Google Maps with:
   - Patient markers (colored circles by severity)
   - Hospital markers (colored squares by status)
   - Info windows on click

---

## Map Features

### Patient Markers
- **Color-coded by severity:**
  - 🔴 Red = Critical
  - 🟠 Orange = High
  - 🟡 Yellow = Medium
  - 🟢 Green = Low
- **Animation:** Critical patients bounce
- **Click:** Shows patient info (name, severity, destination, ETA)

### Hospital Markers
- **Color-coded by status:**
  - 🟢 Green = Available
  - 🟡 Yellow = Limited capacity
  - 🔴 Red = Full
  - ⚫ Gray = Unavailable
- **Shape:** Square (to differentiate from patients)
- **Click:** Shows hospital info (name, capacity, incoming patients)

### Auto-Update
- Map markers update every 5 seconds
- Patient locations move in real-time
- Hospital status colors change based on capacity

---

## Troubleshooting

### Map shows "Map Unavailable"

**Problem:** API key not configured or invalid

**Solution:**
1. Check `.env` file exists in `frontend/web/`
2. Verify `VITE_GOOGLE_MAPS_API_KEY` is set
3. Make sure API key is valid (not expired, not restricted)
4. Restart dev server after adding key

### Map shows "For development purposes only" watermark

**Problem:** API key restrictions or billing not enabled

**Solution:**
1. Go to Google Cloud Console
2. Enable billing on your project
3. Check API key restrictions (should allow localhost)

### Markers not showing

**Problem:** Mock data might have invalid coordinates

**Solution:**
1. Check browser console for errors
2. Verify patient/hospital data has valid `lat`/`lon` or `lat`/`lng`
3. Check that data is being fetched (look for API calls in Network tab)

### Map not loading

**Problem:** Google Maps API script failed to load

**Solution:**
1. Check browser console for errors
2. Verify internet connection
3. Check if Maps JavaScript API is enabled in Google Cloud Console
4. Try a different API key

---

## API Key Security

### Development
- Use `.env` file (never commit to git)
- `.env` is in `.gitignore` by default

### Production
- Set environment variable in hosting platform:
  - Vercel: Project Settings → Environment Variables
  - Netlify: Site Settings → Build & Deploy → Environment
  - AWS: Lambda environment variables
- Restrict API key to your domain in Google Cloud Console

---

## Cost Considerations

### Free Tier
- Google Maps provides $200 free credit per month
- Typical usage for this app: ~$5-20/month
- Monitor usage in Google Cloud Console

### Optimization
- Map loads only once per page
- Markers update without reloading map
- No unnecessary API calls

---

## Alternative: Mock Map (No API Key)

If you don't want to use Google Maps yet, the app will show a fallback message:

```
📍 Map Unavailable
Google Maps API key not configured
Add VITE_GOOGLE_MAPS_API_KEY to .env file
```

All other features (patient list, hospital status, etc.) work without the map.

---

## Next Steps

Once Google Maps is working:
1. Test marker updates (watch them move every 5 seconds)
2. Click markers to see info windows
3. Test with real backend API (when available)
4. Add route polylines (Phase 3)
5. Add directions/navigation (Phase 3)

---

**Need help?** Check the [GOOGLE-MAPS-ACCOUNT-SETUP.md](../../docs/infrastructure/GOOGLE-MAPS-ACCOUNT-SETUP.md) for detailed setup instructions.
