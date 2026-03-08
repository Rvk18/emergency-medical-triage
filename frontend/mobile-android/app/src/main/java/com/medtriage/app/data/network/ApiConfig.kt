package com.medtriage.app.data.network

/**
 * API and Cognito configuration.
 * Set COGNITO_CLIENT_ID (and optionally BASE_URL, COGNITO_REGION) from Terraform outputs:
 *   terraform output -raw cognito_app_client_id
 *   terraform output -raw api_gateway_url
 */
object ApiConfig {
    const val BASE_URL = "https://vrxlwtzfff.execute-api.us-east-1.amazonaws.com/dev"
    const val TRIAGE_PATH = "/triage"

    /** AWS region for Cognito and API (e.g. us-east-1). */
    const val COGNITO_REGION = "us-east-1"

    /**
     * Cognito App Client ID (no secret). From: terraform output -raw cognito_app_client_id
     * Replace with your pool's client ID for real sign-in.
     */
    const val COGNITO_CLIENT_ID = "7unkvq3g553c2k7t4vrupp33bb"

    /** Cognito IdP endpoint for InitiateAuth (no auth header). */
    val COGNITO_BASE_URL: String
        get() = "https://cognito-idp.$COGNITO_REGION.amazonaws.com/"
}
