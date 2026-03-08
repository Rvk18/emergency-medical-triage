package com.medtriage.app.data.network

import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Query

/**
 * RMP Learning API – get question, score answer, my score, leaderboard.
 * Auth: Authorization: Bearer <IdToken> (same as triage/hospitals/route).
 * See docs/frontend/RMP-LEARNING-API.md.
 */
interface RmpLearningApi {

    @POST("rmp/learning")
    suspend fun learning(@Body body: LearningRequestDto): LearningResponseDto

    @GET("rmp/learning/me")
    suspend fun me(): LearningMeDto

    @GET("rmp/learning/leaderboard")
    suspend fun leaderboard(@Query("limit") limit: Int = 20): LearningLeaderboardDto
}

/** POST /rmp/learning body – get_question or score_answer */
data class LearningRequestDto(
    val action: String,
    val topic: String? = null,
    val question: String? = null,
    val reference_answer: String? = null,
    val user_answer: String? = null
)

/** POST /rmp/learning response – get_question */
data class LearningGetQuestionResponseDto(
    val question: String,
    val reference_answer: String,
    val topic: String? = null
)

/** POST /rmp/learning response – score_answer */
data class LearningScoreResponseDto(
    val points: Int,
    val feedback: String? = null
)

/** Unified response: backend returns one of the two shapes; we parse via action. */
data class LearningResponseDto(
    val question: String? = null,
    val reference_answer: String? = null,
    val topic: String? = null,
    val points: Int? = null,
    val feedback: String? = null
)

/** GET /rmp/learning/me */
data class LearningMeDto(
    val total_points: Int = 0,
    val rank: Int? = null
)

/** GET /rmp/learning/leaderboard */
data class LearningLeaderboardDto(
    val leaderboard: List<LeaderboardEntryDto> = emptyList()
)

data class LeaderboardEntryDto(
    val rmp_id: String,
    val total_points: Int,
    val rank: Int
)
