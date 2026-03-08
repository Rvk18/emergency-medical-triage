package com.medtriage.app.data.network

import retrofit2.http.Body
import retrofit2.http.POST

/**
 * Backend POST /route – real driving directions (distance, duration, Google Maps URL).
 */
interface RouteApi {
    @POST("route")
    suspend fun getRoute(@Body body: RouteRequestDto): RouteResponseDto
}

data class RouteRequestDto(
    val origin: RoutePointDto,
    val destination: RoutePointDto
)

data class RoutePointDto(
    val lat: Double? = null,
    val lon: Double? = null,
    val address: String? = null
)

data class RouteResponseDto(
    val distance_km: Double,
    val duration_minutes: Int,
    val directions_url: String? = null
)
