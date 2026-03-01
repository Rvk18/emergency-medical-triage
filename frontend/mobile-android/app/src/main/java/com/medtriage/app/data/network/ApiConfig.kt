package com.medtriage.app.data.network

/**
 * Real API base URL for the emergency medical triage backend.
 * Triage: POST [baseUrl]/triage
 * Use BuildConfig or a different source per build variant if needed later.
 */
object ApiConfig {
    const val BASE_URL = "https://vrxlwtzfff.execute-api.us-east-1.amazonaws.com/dev"
    const val TRIAGE_PATH = "/triage"
}
