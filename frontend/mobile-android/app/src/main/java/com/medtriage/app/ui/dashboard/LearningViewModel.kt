package com.medtriage.app.ui.dashboard

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.medtriage.app.data.rmp.LeaderboardEntry
import com.medtriage.app.data.rmp.LearningMyScore
import com.medtriage.app.data.rmp.LearningQuestion
import com.medtriage.app.data.rmp.LearningScoreResult
import com.medtriage.app.data.rmp.RmpLearningRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject

enum class LearningPhase { Entry, Question, Result, MyScore, Leaderboard }

data class LearningUiState(
    val phase: LearningPhase = LearningPhase.Entry,
    val loading: Boolean = false,
    val error: String? = null,
    val currentQuestion: LearningQuestion? = null,
    val userAnswer: String = "",
    val scoreResult: LearningScoreResult? = null,
    val myScore: LearningMyScore? = null,
    val leaderboard: List<LeaderboardEntry> = emptyList(),
    val selectedTopic: String = "fever protocol"
)

@HiltViewModel
class LearningViewModel @Inject constructor(
    private val repository: RmpLearningRepository
) : ViewModel() {

    private val _state = MutableStateFlow(LearningUiState())
    val state: StateFlow<LearningUiState> = _state.asStateFlow()

    fun toEntry() {
        _state.update {
            it.copy(
                phase = LearningPhase.Entry,
                error = null,
                currentQuestion = null,
                userAnswer = "",
                scoreResult = null,
                myScore = null,
                leaderboard = emptyList()
            )
        }
    }

    fun selectTopic(topic: String) {
        _state.update { it.copy(selectedTopic = topic) }
    }

    fun getQuestion() {
        viewModelScope.launch {
            _state.update { it.copy(loading = true, error = null, phase = LearningPhase.Question) }
            repository.getQuestion(_state.value.selectedTopic).fold(
                onSuccess = { q ->
                    _state.update {
                        it.copy(
                            loading = false,
                            currentQuestion = q,
                            userAnswer = "",
                            scoreResult = null
                        )
                    }
                },
                onFailure = { e ->
                    _state.update {
                        it.copy(loading = false, error = e.message ?: "Failed to load question")
                    }
                }
            )
        }
    }

    fun setUserAnswer(answer: String) {
        _state.update { it.copy(userAnswer = answer) }
    }

    fun submitAnswer() {
        val q = _state.value.currentQuestion ?: return
        val answer = _state.value.userAnswer.trim()
        if (answer.isBlank()) return
        viewModelScope.launch {
            _state.update { it.copy(loading = true, error = null) }
            repository.scoreAnswer(q.question, q.referenceAnswer, answer).fold(
                onSuccess = { result ->
                    _state.update {
                        it.copy(
                            loading = false,
                            phase = LearningPhase.Result,
                            scoreResult = result
                        )
                    }
                },
                onFailure = { e ->
                    _state.update {
                        it.copy(loading = false, error = e.message ?: "Failed to score")
                    }
                }
            )
        }
    }

    fun loadMyScore() {
        viewModelScope.launch {
            _state.update { it.copy(loading = true, error = null, phase = LearningPhase.MyScore) }
            repository.getMyScore().fold(
                onSuccess = { score ->
                    _state.update { it.copy(loading = false, myScore = score) }
                },
                onFailure = { e ->
                    _state.update {
                        it.copy(loading = false, error = e.message ?: "Failed to load score")
                    }
                }
            )
        }
    }

    fun loadLeaderboard() {
        viewModelScope.launch {
            _state.update { it.copy(loading = true, error = null, phase = LearningPhase.Leaderboard) }
            repository.getLeaderboard(limit = 20).fold(
                onSuccess = { list ->
                    _state.update { it.copy(loading = false, leaderboard = list) }
                },
                onFailure = { e ->
                    _state.update {
                        it.copy(loading = false, error = e.message ?: "Failed to load leaderboard")
                    }
                }
            )
        }
    }

    fun clearError() {
        _state.update { it.copy(error = null) }
    }
}
