package com.medtriage.app.data.triage

import javax.inject.Inject
import javax.inject.Singleton

/**
 * Holds the last triage result for use by the Hospitals flow (POST /hospitals needs severity, recommendations, session_id).
 */
@Singleton
class TriageSessionHolder @Inject constructor() {
    @Volatile
    var lastSeverity: SeverityLevel? = null
        private set
    @Volatile
    var lastRecommendations: List<String> = emptyList()
        private set
    @Volatile
    var lastSessionId: String? = null
        private set

    fun setFromResult(result: TriageResult) {
        lastSeverity = result.severity
        lastRecommendations = result.recommendedActions
        lastSessionId = result.sessionId
    }

    fun clear() {
        lastSeverity = null
        lastRecommendations = emptyList()
        lastSessionId = null
    }
}
