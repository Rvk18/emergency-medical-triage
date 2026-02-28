package com.medtriage.app.data.rmp

import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.flow
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class RmpRepository @Inject constructor() {

    fun getProfile(): kotlinx.coroutines.flow.Flow<Result<RmpProfile>> = flow {
        delay(500)
        emit(Result.success(RmpProfile(
            id = "rmp1",
            competencyScore = 72,
            casesCompleted = 45,
            successRatePercent = 88,
            levelBadge = "Level 3",
            recentCases = listOf(
                RecentCase("c1", "Chest pain assessment", "HIGH", "Today"),
                RecentCase("c2", "Trauma triage", "MEDIUM", "Yesterday")
            )
        )))
    }

    fun getGuidance(emergencyId: String): kotlinx.coroutines.flow.Flow<Result<List<GuidanceStep>>> = flow {
        delay(300)
        emit(Result.success(listOf(
            GuidanceStep(1, "Ensure scene safety", "Check that the area is safe for you and the patient."),
            GuidanceStep(2, "Assess responsiveness", "Use AVPU scale to check consciousness."),
            GuidanceStep(3, "Call for help if needed", "If critical, request backup or telemedicine.")
        )))
    }

    fun getLearningModules(): kotlinx.coroutines.flow.Flow<Result<List<LearningModule>>> = flow {
        delay(400)
        emit(Result.success(listOf(
            LearningModule("m1", "Basic CPR", 100, true),
            LearningModule("m2", "Bleeding control", 60, false),
            LearningModule("m3", "Shock management", 0, false)
        )))
    }
}
