package com.medtriage.app.data.triage

data class PatientInfo(
    val age: Int? = null,
    val gender: String? = null,
    val locationLat: Double? = null,
    val locationLng: Double? = null,
    val medicalHistory: String? = null,
    val allergies: String? = null
)

data class SymptomInput(
    val primarySymptoms: List<String> = emptyList(),
    val freeText: String = "",
    val durationMinutes: Int? = null,
    val patientReportedSeverity: String? = null
)

data class VitalsInput(
    val heartRateBpm: Int? = null,
    val bloodPressureSystolic: Int? = null,
    val bloodPressureDiastolic: Int? = null,
    val temperatureCelsius: Float? = null,
    val spo2Percent: Int? = null,
    val respiratoryRatePerMin: Int? = null,
    val consciousnessAvpu: String? = null
)

enum class SeverityLevel { CRITICAL, HIGH, MEDIUM, LOW }

data class TriageResult(
    val emergencyId: String,
    val severity: SeverityLevel,
    val confidencePercent: Int,
    val recommendedActions: List<String>,
    val safetyDisclaimers: List<String>,
    val flaggedForReview: Boolean
)
