package com.medtriage.app.data.hospitals

import com.medtriage.app.data.network.HospitalDto
import com.medtriage.app.data.network.HospitalsApi
import com.medtriage.app.data.network.HospitalsRequestDto
import com.medtriage.app.data.network.RouteApi
import com.medtriage.app.data.network.RoutePointDto
import com.medtriage.app.data.network.RouteRequestDto
import com.medtriage.app.data.triage.SeverityLevel
import com.medtriage.app.data.triage.TriageSessionHolder
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import kotlinx.coroutines.withContext
import java.io.IOException
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class HospitalRepository @Inject constructor(
    private val hospitalsApi: HospitalsApi,
    private val routeApi: RouteApi,
    private val triageSessionHolder: TriageSessionHolder
) {

    fun getMatches(): Flow<Result<List<HospitalMatch>>> = flow {
        val severity = triageSessionHolder.lastSeverity
        val recommendations = triageSessionHolder.lastRecommendations
        val sessionId = triageSessionHolder.lastSessionId
        if (severity != null && recommendations.isNotEmpty()) {
            try {
                val response = withContext(Dispatchers.IO) {
                    hospitalsApi.getHospitals(
                        HospitalsRequestDto(
                            severity = severityToApi(severity),
                            recommendations = recommendations,
                            limit = 3,
                            session_id = sessionId
                        )
                    )
                }
                val list = response.hospitals.mapIndexed { i, dto -> dto.toHospitalMatch(i) }
                emit(Result.success(list))
            } catch (e: IOException) {
                emit(Result.failure(IOException("Hospitals API error: ${e.message}", e)))
            } catch (e: retrofit2.HttpException) {
                emit(Result.failure(IOException("Hospitals API ${e.code()}: ${e.response()?.errorBody()?.string()}", e)))
            } catch (e: Exception) {
                emit(Result.failure(e))
            }
        } else {
            emit(Result.failure(IllegalArgumentException("Missing triage severity or recommendations. Cannot match hospitals.")))
        }
    }

    suspend fun getRoute(
        originLat: Double,
        originLon: Double,
        destLat: Double,
        destLon: Double
    ): Result<RouteResult> = withContext(Dispatchers.IO) {
        try {
            val response = routeApi.getRoute(
                RouteRequestDto(
                    origin = RoutePointDto(lat = originLat, lon = originLon),
                    destination = RoutePointDto(lat = destLat, lon = destLon)
                )
            )
            Result.success(
                RouteResult(
                    distanceKm = response.distance_km,
                    durationMinutes = response.duration_minutes,
                    directionsUrl = response.directions_url
                )
            )
        } catch (e: IOException) {
            Result.failure(IOException("Route API error: ${e.message}", e))
        } catch (e: retrofit2.HttpException) {
            Result.failure(IOException("Route API ${e.code()}", e))
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    fun getRouteSteps(hospitalId: String): Flow<Result<List<RouteStep>>> = flow {
        delay(500)
        emit(Result.success(listOf(
            RouteStep("Head north on Main Rd", 500),
            RouteStep("Turn right at Health St", 1200),
            RouteStep("Destination on the left", null)
        )))
    }

    private fun severityToApi(s: SeverityLevel): String = when (s) {
        SeverityLevel.CRITICAL -> "critical"
        SeverityLevel.HIGH -> "high"
        SeverityLevel.MEDIUM -> "medium"
        SeverityLevel.LOW -> "low"
    }

    private fun HospitalDto.toHospitalMatch(index: Int): HospitalMatch = HospitalMatch(
        id = "h_${index}_${name.hashCode()}",
        name = name,
        distanceKm = distance_km ?: 0.0,
        etaMinutes = (distance_km?.times(3)?.toInt() ?: 15).coerceAtLeast(5),
        bedsAvailable = 0,
        bedsTotal = 0,
        specialistOnCall = true,
        matchScorePercent = (match_score?.times(100)?.toInt() ?: 80).coerceIn(0, 100),
        lat = lat,
        lon = lon
    )

    private fun mockMatches(): List<HospitalMatch> = listOf(
        HospitalMatch("h1", "City General Hospital", 2.5, 8, 12, 50, true, 92, 12.97, 77.59),
        HospitalMatch("h2", "Rural Care Center", 5.0, 15, 5, 20, false, 78, 12.95, 77.55),
        HospitalMatch("h3", "District Medical College", 7.2, 22, 8, 30, true, 85, 13.0, 77.6)
    )
}
