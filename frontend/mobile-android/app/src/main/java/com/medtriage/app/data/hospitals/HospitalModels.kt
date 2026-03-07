package com.medtriage.app.data.hospitals

data class HospitalMatch(
    val id: String,
    val name: String,
    val distanceKm: Double,
    val etaMinutes: Int,
    val bedsAvailable: Int,
    val bedsTotal: Int,
    val specialistOnCall: Boolean,
    val matchScorePercent: Int,
    val lat: Double? = null,
    val lon: Double? = null
)

/** Result of POST /route – real directions from backend. */
data class RouteResult(
    val distanceKm: Double,
    val durationMinutes: Int,
    val directionsUrl: String?
)

data class RouteStep(
    val instruction: String,
    val distanceMeters: Int?
)
