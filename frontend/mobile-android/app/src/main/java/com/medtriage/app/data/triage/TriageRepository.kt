package com.medtriage.app.data.triage

import com.medtriage.app.data.network.TriageApi
import com.medtriage.app.data.network.TriageRequestDto
import com.medtriage.app.data.network.TriageResponseDto
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import java.io.IOException
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class TriageRepository @Inject constructor(
    private val triageApi: TriageApi
) {

    /**
     * Calls real backend POST /triage for functional testing.
     * Maps app models to backend request; maps response to TriageResult.
     */
    fun assess(
        patientInfo: PatientInfo,
        symptoms: SymptomInput,
        vitals: VitalsInput
    ): Flow<Result<TriageResult>> = flow {
        val requestDto = toRequestDto(patientInfo, symptoms, vitals)
        if (requestDto.symptoms.isEmpty()) {
            emit(Result.failure(IllegalArgumentException("At least one symptom is required")))
            return@flow
        }
        try {
            val responseDto = triageApi.assess(requestDto)
            emit(Result.success(toTriageResult(responseDto)))
        } catch (e: IOException) {
            emit(Result.failure(IOException("Network error: ${e.message}", e)))
        } catch (e: retrofit2.HttpException) {
            val body = e.response()?.errorBody()?.string() ?: e.message()
            emit(Result.failure(IOException("Triage API error ${e.code()}: $body", e)))
        } catch (e: Exception) {
            emit(Result.failure(e))
        }
    }

    private fun toRequestDto(
        patientInfo: PatientInfo,
        symptoms: SymptomInput,
        vitals: VitalsInput
    ): TriageRequestDto {
        val symptomList = buildList {
            addAll(symptoms.primarySymptoms)
            if (symptoms.freeText.isNotBlank()) {
                addAll(symptoms.freeText.split(",").map { it.trim() }.filter { it.isNotBlank() })
            }
        }.distinct()
        val vitalsMap = buildMap<String, Float> {
            vitals.heartRateBpm?.toFloat()?.let { put("heart_rate", it) }
            vitals.bloodPressureSystolic?.toFloat()?.let { put("bp", it) }
            vitals.spo2Percent?.toFloat()?.let { put("spo2", it) }
            vitals.temperatureCelsius?.let { put("temp_c", it) }
            vitals.respiratoryRatePerMin?.toFloat()?.let { put("respiratory_rate", it) }
        }
        return TriageRequestDto(
            symptoms = symptomList,
            vitals = vitalsMap,
            age_years = patientInfo.age,
            sex = patientInfo.gender
        )
    }

    private fun toTriageResult(dto: TriageResponseDto): TriageResult {
        val severity = when (dto.severity.lowercase()) {
            "critical" -> SeverityLevel.CRITICAL
            "high" -> SeverityLevel.HIGH
            "medium" -> SeverityLevel.MEDIUM
            "low" -> SeverityLevel.LOW
            else -> SeverityLevel.MEDIUM
        }
        return TriageResult(
            emergencyId = "tri_${System.currentTimeMillis()}",
            severity = severity,
            confidencePercent = (dto.confidence * 100).toInt().coerceIn(0, 100),
            recommendedActions = dto.recommendations,
            safetyDisclaimers = listOfNotNull(dto.safety_disclaimer),
            flaggedForReview = dto.force_high_priority
        )
    }
}
