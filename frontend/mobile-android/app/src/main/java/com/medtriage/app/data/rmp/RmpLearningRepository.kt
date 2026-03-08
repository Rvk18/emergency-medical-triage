package com.medtriage.app.data.rmp

import com.medtriage.app.data.network.LearningLeaderboardDto
import com.medtriage.app.data.network.LearningMeDto
import com.medtriage.app.data.network.LearningRequestDto
import com.medtriage.app.data.network.LearningResponseDto
import com.medtriage.app.data.network.RmpLearningApi
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.io.IOException
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class RmpLearningRepository @Inject constructor(
    private val api: RmpLearningApi
) {

    suspend fun getQuestion(topic: String = "general"): Result<LearningQuestion> = withContext(Dispatchers.IO) {
        try {
            val response = api.learning(
                LearningRequestDto(action = "get_question", topic = topic)
            )
            val q = response.question
            val ref = response.reference_answer
            if (q.isNullOrBlank() || ref.isNullOrBlank()) {
                Result.failure(IOException("Invalid get_question response"))
            } else {
                Result.success(LearningQuestion(question = q, referenceAnswer = ref, topic = response.topic))
            }
        } catch (e: retrofit2.HttpException) {
            if (e.code() == 504) Result.failure(IOException("Service busy, try again", e))
            else Result.failure(IOException("API ${e.code()}: ${e.message()}", e))
        } catch (e: Exception) {
            Result.failure(IOException("Learning error: ${e.message}", e))
        }
    }

    suspend fun scoreAnswer(
        question: String,
        referenceAnswer: String,
        userAnswer: String
    ): Result<LearningScoreResult> = withContext(Dispatchers.IO) {
        try {
            val response = api.learning(
                LearningRequestDto(
                    action = "score_answer",
                    question = question,
                    reference_answer = referenceAnswer,
                    user_answer = userAnswer
                )
            )
            val points = response.points ?: 0
            Result.success(LearningScoreResult(points = points, feedback = response.feedback ?: ""))
        } catch (e: retrofit2.HttpException) {
            if (e.code() == 504) Result.failure(IOException("Service busy, try again", e))
            else Result.failure(IOException("API ${e.code()}: ${e.message()}", e))
        } catch (e: Exception) {
            Result.failure(IOException("Score error: ${e.message}", e))
        }
    }

    suspend fun getMyScore(): Result<LearningMyScore> = withContext(Dispatchers.IO) {
        try {
            val response: LearningMeDto = api.me()
            Result.success(
                LearningMyScore(
                    totalPoints = response.total_points,
                    rank = response.rank
                )
            )
        } catch (e: retrofit2.HttpException) {
            Result.failure(IOException("API ${e.code()}: ${e.message()}", e))
        } catch (e: Exception) {
            Result.failure(IOException("My score error: ${e.message}", e))
        }
    }

    suspend fun getLeaderboard(limit: Int = 20): Result<List<LeaderboardEntry>> = withContext(Dispatchers.IO) {
        try {
            val response: LearningLeaderboardDto = api.leaderboard(limit = limit)
            Result.success(
                response.leaderboard.map { e ->
                    LeaderboardEntry(rank = e.rank, totalPoints = e.total_points, rmpId = e.rmp_id)
                }
            )
        } catch (e: retrofit2.HttpException) {
            Result.failure(IOException("API ${e.code()}: ${e.message()}", e))
        } catch (e: Exception) {
            Result.failure(IOException("Leaderboard error: ${e.message}", e))
        }
    }
}

data class LearningQuestion(
    val question: String,
    val referenceAnswer: String,
    val topic: String?
)

data class LearningScoreResult(
    val points: Int,
    val feedback: String
)

data class LearningMyScore(
    val totalPoints: Int,
    val rank: Int?
)

data class LeaderboardEntry(
    val rank: Int,
    val totalPoints: Int,
    val rmpId: String
)
