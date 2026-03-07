# Google Maps Backend Integration - Complete

## Architecture

The Google Maps API key is now fetched from AWS Secrets Manager through a secure backend API endpoint.

```
┌─────────────────────────────────────────────────────────────┐
│                    AWS Secrets Manager                       │
│              google-maps-config secret                       │
│                  { api_key: "AIza..." }                      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ boto3.get_secret_value()
                         ↓
┌─────────────────────────────────────────────────────────────┐
│              Backend Lambda (config_lambda)                  │
│                  GET /config endpoint                        │
│         Returns: { google_maps_api_key: "..." }             │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ HTTP GET /config
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                  Frontend (Browser)                          │
│              src/services/config.js                          │
│         Fetches key and loads Google Maps                    │
└─────────────────────────────────────────────────────────────┘
```

---

## What Was Implemented

### 1. Backend Lambda Function ✅

**File:** `infrastructure/config_lambda_src/lambda_handler.py`

```python
def handler(event, context):
    # Fetch Google Maps API key from Secrets Manager
    api_key = get_google_maps_api_key()
    
    return {
        "statusCode": 200,
        "body": json.dumps({
            "google_maps_api_key": api_key,
            "environment": "dev"
        })
    }
```

**Features:**
- Fetches key from AWS Secrets Manager using boto3
- Returns JSON response with API key
- CORS enabled for frontend access
- Error handling with fallback

### 2. Terraform Configuration ✅

**File:** `infrastructure/config.tf`

```hcl
resource "aws_lambda_function" "config" {
  function_name = "${var.name_prefix}-config"
  handler       = "lambda_handler.handler"
  runtime       = "python3.12"
  
  environment {
    variables = {
      GOOGLE_MAPS_CONFIG_SECRET_NAME = aws_secretsmanager_secret.google_maps_config[0].name
    }
  }
}

resource "aws_apigatewayv2_route" "config" {
  route_key = "GET /config"
  target    = "integrations/${aws_apigatewayv2_integration.config.id}"
}
```

**Features:**
- Lambda function with Secrets Manager access
- API Gateway route `GET /config`
- IAM permissions to read secret
- CloudWatch logging

### 3. Frontend Config Service ✅

**File:** `src/services/config.js`

```javascript
export async function fetchConfig() {
  const response = await fetch(`${API_URL}/config`);
  const config = await response.json();
  return config;
}

export async function getGoogleMapsApiKey() {
  const config = await fetchConfig();
  return config.google_maps_api_key;
}
```

**Features:**
- Fetches config from backend API
- Caches config to avoid repeated calls
- Error handling with fallback
- Clean API for other services

### 4. Updated Google Maps Utility ✅

**File:** `src/utils/google-maps.js`

```javascript
export async function loadGoogleMaps() {
  // Fetch API key from backend
  const apiKey = await getGoogleMapsApiKey();
  
  // Load Google Maps script
  const script = document.createElement('script');
  script.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}`;
  document.head.appendChild(script);
}
```

**Features:**
- Fetches key dynamically from backend
- No hardcoded keys in frontend
- Graceful error handling
- Same map features as before

---

## Deployment Steps

### 1. Deploy Backend Infrastructure

```bash
cd infrastructure

# Ensure Google Maps API key is in terraform.tfvars
# google_maps_api_key = "AIza...your_actual_key"

# Deploy
terraform apply
```

This creates:
- ✅ Config Lambda function
- ✅ GET /config API route
- ✅ IAM permissions for Secrets Manager
- ✅ CloudWatch log group

### 2. Test the Endpoint

```bash
# Get API URL
API_URL=$(terraform output -raw api_gateway_url)

# Test config endpoint
curl -s "${API_URL}/config" | jq

# Expected output:
# {
#   "google_maps_api_key": "AIza...your_key",
#   "environment": "dev"
# }
```

### 3. Start Frontend

```bash
cd ../frontend/web

# No .env changes needed!
npm run dev
```

### 4. Verify

1. Open http://localhost:5173
2. Login
3. Go to Dashboard
4. Check browser console for:
   ```
   [Config] Fetching configuration from backend
   [Config] Configuration loaded successfully
   [GoogleMaps] API key retrieved, loading Maps script
   [GoogleMaps] API loaded successfully
   ```
5. Map should display with markers

---

## Security Benefits

### ✅ No Secrets in Frontend Code
- API key never stored in `.env` files
- No hardcoded keys in JavaScript
- Key not visible in source code or git

### ✅ Backend Controls Access
- Lambda has IAM permissions to read secret
- Frontend cannot directly access Secrets Manager
- Backend can add authentication/rate limiting

### ✅ Dynamic Configuration
- Key can be rotated without frontend changes
- Different keys for dev/staging/prod
- Easy to update via Terraform

### ✅ Audit Trail
- CloudWatch logs all config requests
- Can track who accessed the key
- Monitor for unusual access patterns

---

## Troubleshooting

### Map shows "Map Unavailable"

**Problem:** Backend not returning API key

**Check:**
```bash
# Test config endpoint
curl -s "${API_URL}/config" | jq

# Check Lambda logs
aws logs tail /aws/lambda/emergency-medical-triage-dev-config --follow
```

**Solutions:**
1. Verify Terraform deployed successfully
2. Check Google Maps secret exists in Secrets Manager
3. Verify Lambda has IAM permissions
4. Check API Gateway route is configured

### Config endpoint returns 404

**Problem:** Route not deployed

**Solution:**
```bash
cd infrastructure
terraform apply
```

### Config endpoint returns 500

**Problem:** Lambda error

**Check logs:**
```bash
aws logs tail /aws/lambda/emergency-medical-triage-dev-config --follow
```

**Common issues:**
- Secret name environment variable not set
- IAM permissions missing
- Secret doesn't exist

---

## Files Created/Modified

### New Files
- ✅ `infrastructure/config_lambda_src/lambda_handler.py` - Backend Lambda
- ✅ `infrastructure/config.tf` - Terraform configuration
- ✅ `src/services/config.js` - Frontend config service
- ✅ `GOOGLE-MAPS-BACKEND-INTEGRATION.md` - This document

### Modified Files
- ✅ `src/utils/google-maps.js` - Fetch key from backend
- ✅ `GOOGLE-MAPS-SETUP.md` - Updated setup guide

---

## Next Steps

1. **Deploy backend:** `cd infrastructure && terraform apply`
2. **Test endpoint:** `curl ${API_URL}/config`
3. **Start frontend:** `cd frontend/web && npm run dev`
4. **Verify map loads** in browser

---

**Status:** ✅ Complete - Ready for deployment
