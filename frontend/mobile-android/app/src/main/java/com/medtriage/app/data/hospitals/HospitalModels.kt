package com.medtriage.app.data.hospitals

data class HospitalMatch(
    val id: String,
    val name: String,
    val distanceKm: Double,
    val etaMinutes: Int,
    val bedsAvailable: Int,
    val bedsTotal: Int,
    val specialistOnCall: Boolean,
    val matchScorePercent: Int
)

data class RouteStep(
    val instruction: String,
    val distanceMeters: Int?
)
