package com.medtriage.app.data.rmp

data class RmpProfile(
    val id: String,
    val competencyScore: Int,
    val casesCompleted: Int,
    val successRatePercent: Int,
    val levelBadge: String,
    val recentCases: List<RecentCase> = emptyList()
)

data class RecentCase(
    val id: String,
    val summary: String,
    val severity: String,
    val date: String
)

data class GuidanceStep(
    val number: Int,
    val title: String,
    val description: String
)

data class LearningModule(
    val id: String,
    val title: String,
    val progressPercent: Int,
    val completed: Boolean
)
