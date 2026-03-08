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
import kotlinx.coroutines.flow.catch
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

    /**
     * Get hospital matches. When [patientLocationLat] and [patientLocationLon] are provided,
     * backend returns distance_km, duration_minutes, directions_url per hospital (routing agent).
     */
    fun getMatches(
        patientLocationLat: Double? = null,
        patientLocationLon: Double? = null
    ): Flow<Result<List<HospitalMatch>>> = flow {
        val severity = triageSessionHolder.lastSeverity
        val recommendations = triageSessionHolder.lastRecommendations
        val sessionId = triageSessionHolder.lastSessionId
        if (severity == null || recommendations.isEmpty()) {
            emit(Result.failure(IllegalArgumentException("Missing triage severity or recommendations. Cannot match hospitals.")))
            return@flow
        }
        val response = withContext(Dispatchers.IO) {
            hospitalsApi.getHospitals(
                HospitalsRequestDto(
                    severity = severityToApi(severity),
                    recommendations = recommendations,
                    limit = 3,
                    session_id = sessionId,
                    patient_location_lat = patientLocationLat,
                    patient_location_lon = patientLocationLon
                )
            )
        }
        val list = response.hospitals.mapIndexed { i, dto -> dto.toHospitalMatch(i) }
        emit(Result.success(list))
    }.catch { e ->
        emit(Result.failure(IOException("Hospitals API error: ${e.message}", e)))
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
                    distanceKm = response.distance_km ?: 0.0,
                    durationMinutes = response.duration_minutes?.toInt()?.coerceAtLeast(0) ?: 0,
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

    /** Fallback coordinates when backend does not return lat/lon (e.g. blr-apollo-1). Enables route/directions. */
    private fun fallbackCoordsForHospital(hospitalId: String?): Pair<Double, Double>? = when (hospitalId) {
        "blr-apollo-1" -> 12.8967 to 77.5982   // Apollo Hospital, Bannerghatta Road
        "blr-narayana-1" -> 12.9095 to 77.6830 // Narayana Health City
        "blr-victoria-1" -> 12.9650 to 77.5930 // Victoria Hospital
        else -> null
    }

    private fun HospitalDto.toHospitalMatch(index: Int): HospitalMatch {
        val (fallbackLat, fallbackLon) = fallbackCoordsForHospital(hospital_id) ?: (null to null)
        return HospitalMatch(
            id = hospital_id ?: "h_${index}_${name.hashCode()}",
            name = name,
            distanceKm = distance_km ?: 0.0,
            etaMinutes = duration_minutes?.toInt()?.coerceAtLeast(1) ?: (distance_km?.times(3)?.toInt() ?: 15).coerceAtLeast(5),
            bedsAvailable = 0,
            bedsTotal = 0,
            specialistOnCall = true,
            matchScorePercent = (match_score?.times(100)?.toInt() ?: 80).coerceIn(0, 100),
            lat = lat ?: fallbackLat,
            lon = lon ?: fallbackLon
        )
    }

    private fun mockMatches(): List<HospitalMatch> = listOf(
        HospitalMatch("h1", "City General Hospital", 2.5, 8, 12, 50, true, 92, 12.97, 77.59),
        HospitalMatch("h2", "Rural Care Center", 5.0, 15, 5, 20, false, 78, 12.95, 77.55),
        HospitalMatch("h3", "District Medical College", 7.2, 22, 8, 30, true, 85, 13.0, 77.6)
    )
}
