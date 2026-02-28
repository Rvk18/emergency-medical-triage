package com.medtriage.app.data.triage

import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class TriageRepository @Inject constructor() {

    fun assess(
        patientInfo: PatientInfo,
        symptoms: SymptomInput,
        vitals: VitalsInput
    ): Flow<Result<TriageResult>> = flow {
        delay(1500) // Simulate API delay
        val result = TriageResult(
            emergencyId = "tri_${System.currentTimeMillis()}",
            severity = SeverityLevel.MEDIUM,
            confidencePercent = 88,
            recommendedActions = listOf(
                "Monitor vital signs continuously",
                "Ensure patient is in a comfortable position",
                "Prepare for possible hospital transfer"
            ),
            safetyDisclaimers = listOf(
                "This assessment is AI-assisted and must be verified by a qualified healthcare professional.",
                "In case of deterioration, seek immediate medical attention."
            ),
            flaggedForReview = false
        )
        emit(Result.success(result))
    }
}
