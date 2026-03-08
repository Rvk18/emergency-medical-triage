package com.medtriage.app.data.network

import retrofit2.http.Body
import retrofit2.http.POST

/**
 * Backend POST /hospitals – get hospital recommendations by severity and recommendations.
 */
interface HospitalsApi {
    @POST("hospitals")
    suspend fun getHospitals(@Body body: HospitalsRequestDto): HospitalsResponseDto
}

data class HospitalsRequestDto(
    val severity: String,
    val recommendations: List<String>,
    val limit: Int = 3,
    val session_id: String? = null,
    val patient_location_lat: Double? = null,
    val patient_location_lon: Double? = null
)

data class HospitalsResponseDto(
    val hospitals: List<HospitalDto> = emptyList(),
    val safety_disclaimer: String? = null
)

data class HospitalDto(
    val hospital_id: String? = null,
    val name: String,
    val match_score: Double? = null,
    val match_reasons: List<String>? = null,
    val lat: Double? = null,
    val lon: Double? = null,
    val distance_km: Double? = null,
    val duration_minutes: Double? = null,
    val address: String? = null
)
