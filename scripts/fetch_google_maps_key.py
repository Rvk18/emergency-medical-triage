#!/usr/bin/env python3
"""
Fetch Google Maps API key from AWS Secrets Manager and update .env file.

Usage:
    python scripts/fetch_google_maps_key.py
"""

import boto3
import json
import os
import sys

def fetch_api_key():
    """Fetch Google Maps API key from AWS Secrets Manager."""
    try:
        client = boto3.client('secretsmanager', region_name='us-east-1')
        response = client.get_secret_value(
            SecretId='emergency-medical-triage-dev/google-maps-config'
        )
        secret = json.loads(response['SecretString'])
        api_key = secret.get('api_key', '').strip()
        
        if not api_key:
            print("❌ Error: 'api_key' not found in secret")
            return None
            
        print(f"✅ Successfully fetched API key from Secrets Manager")
        return api_key
        
    except Exception as e:
        print(f"❌ Error fetching secret: {e}")
        return None

def update_env_file(api_key):
    """Update the .env file with the API key."""
    env_path = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'web', '.env')
    
    if not os.path.exists(env_path):
        print(f"❌ Error: .env file not found at {env_path}")
        return False
    
    try:
        # Read existing .env content
        with open(env_path, 'r') as f:
            lines = f.readlines()
        
        # Update or add the Google Maps API key line
        updated = False
        new_lines = []
        
        for line in lines:
            if line.startswith('VITE_GOOGLE_MAPS_API_KEY='):
                new_lines.append(f'VITE_GOOGLE_MAPS_API_KEY={api_key}\n')
                updated = True
            else:
                new_lines.append(line)
        
        # If key wasn't found, add it
        if not updated:
            new_lines.append(f'\nVITE_GOOGLE_MAPS_API_KEY={api_key}\n')
        
        # Write back to file
        with open(env_path, 'w') as f:
            f.writelines(new_lines)
        
        print(f"✅ Updated .env file at {env_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error updating .env file: {e}")
        return False

def main():
    print("🔑 Fetching Google Maps API key from AWS Secrets Manager...")
    print()
    
    # Fetch the API key
    api_key = fetch_api_key()
    if not api_key:
        sys.exit(1)
    
    print(f"📝 API Key: {api_key[:20]}...{api_key[-10:]}")
    print()
    
    # Update .env file
    if update_env_file(api_key):
        print()
        print("✨ Done! Google Maps API key has been added to .env file")
        print("🚀 Restart your dev server to use the new key")
    else:
        sys.exit(1)

if __name__ == '__main__':
    main()
