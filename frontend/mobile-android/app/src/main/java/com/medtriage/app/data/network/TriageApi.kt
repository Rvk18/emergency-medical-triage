package com.medtriage.app.data.network

import retrofit2.http.Body
import retrofit2.http.POST

/**
 * Backend triage API (POST /triage).
 * Request/response match backend TriageRequest and TriageResult in src/triage/models/triage.py.
 */
interface TriageApi {

    @POST("triage")
    suspend fun assess(@Body body: TriageRequestDto): TriageResponseDto
}

/** Request body for POST /triage. */
data class TriageRequestDto(
    val symptoms: List<String>,
    val vitals: Map<String, Float> = emptyMap(),
    val age_years: Int? = null,
    val sex: String? = null
)

/** Response body from POST /triage. */
data class TriageResponseDto(
    val severity: String,
    val confidence: Double,
    val recommendations: List<String>,
    val force_high_priority: Boolean = false,
    val safety_disclaimer: String? = null
)
