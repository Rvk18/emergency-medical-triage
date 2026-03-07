"""
Config API Lambda: Returns frontend configuration including Google Maps API key.

GET /config
Returns: { google_maps_api_key: string }

This endpoint is public (no auth required) because:
1. Google Maps API keys are designed to be used client-side
2. The key is restricted by domain/referrer in Google Cloud Console
3. It's standard practice to expose Maps API keys in frontend code
"""

import json
import logging
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def _get_google_maps_api_key() -> str | None:
    """Fetch Google Maps API key from Secrets Manager."""
    secret_name = os.environ.get("GOOGLE_MAPS_CONFIG_SECRET_NAME", "").strip()
    if not secret_name:
        logger.warning("GOOGLE_MAPS_CONFIG_SECRET_NAME not set")
        return None
    
    try:
        import boto3
        client = boto3.client("secretsmanager")
        response = client.get_secret_value(SecretId=secret_name)
        secret_data = json.loads(response["SecretString"])
        api_key = secret_data.get("api_key", "").strip()
        
        if not api_key:
            logger.warning("api_key not found in secret")
            return None
            
        logger.info("Successfully retrieved Google Maps API key")
        return api_key
        
    except Exception as e:
        logger.error(f"Failed to retrieve Google Maps API key: {e}")
        return None


def handler(event: dict, context: object) -> dict:
    """
    API Gateway Lambda handler for GET /config.
    Returns frontend configuration.
    """
    logger.info(f"Config request: {json.dumps(event)}")
    
    try:
        # Fetch Google Maps API key
        google_maps_api_key = _get_google_maps_api_key()
        
        # Build response
        config = {
            "google_maps_api_key": google_maps_api_key,
            "environment": os.environ.get("ENVIRONMENT", "dev")
        }
        
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",  # CORS
                "Access-Control-Allow-Methods": "GET, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type"
            },
            "body": json.dumps(config)
        }
        
    except Exception as e:
        logger.error(f"Config handler error: {e}", exc_info=True)
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "error": "Internal server error",
                "message": str(e)
            })
        }
