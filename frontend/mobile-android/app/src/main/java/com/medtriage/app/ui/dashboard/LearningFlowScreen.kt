package com.medtriage.app.ui.dashboard

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.FilterChip
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import com.medtriage.app.data.rmp.LeaderboardEntry
import com.medtriage.app.data.rmp.LearningMyScore
import com.medtriage.app.data.rmp.LearningScoreResult
import com.medtriage.app.ui.theme.Spacing

private val TOPICS = listOf(
    "fever protocol",
    "diabetes management",
    "acute diarrhoea",
    "general"
)

@Composable
fun LearningFlowScreen(
    onBack: () -> Unit,
    viewModel: LearningViewModel = hiltViewModel()
) {
    val state by viewModel.state.collectAsState()

    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(Spacing.screenHorizontal)
            .verticalScroll(rememberScrollState())
    ) {
        TextButton(onClick = onBack) {
            Text("← Back to Dashboard")
        }
        state.error?.let { err ->
            Text(err, color = MaterialTheme.colorScheme.error, style = MaterialTheme.typography.bodySmall)
            TextButton(onClick = { viewModel.clearError() }) { Text("Dismiss") }
        }
        when (state.phase) {
            LearningPhase.Entry -> LearningEntryContent(
                selectedTopic = state.selectedTopic,
                onTopicSelect = viewModel::selectTopic,
                onStartQuiz = viewModel::getQuestion,
                onMyScore = viewModel::loadMyScore,
                onLeaderboard = viewModel::loadLeaderboard
            )
            LearningPhase.Question -> LearningQuestionContent(
                question = state.currentQuestion?.question ?: "",
                userAnswer = state.userAnswer,
                onAnswerChange = viewModel::setUserAnswer,
                onSubmit = viewModel::submitAnswer,
                loading = state.loading,
                onBack = viewModel::toEntry
            )
            LearningPhase.Result -> LearningResultContent(
                scoreResult = state.scoreResult,
                onNextQuestion = viewModel::getQuestion,
                onBack = viewModel::toEntry
            )
            LearningPhase.MyScore -> LearningMyScoreContent(
                myScore = state.myScore,
                loading = state.loading,
                onBack = viewModel::toEntry
            )
            LearningPhase.Leaderboard -> LearningLeaderboardContent(
                leaderboard = state.leaderboard,
                loading = state.loading,
                onBack = viewModel::toEntry
            )
        }
        Spacer(Modifier.height(Spacing.space40))
    }
}

@OptIn(ExperimentalLayoutApi::class)
@Composable
private fun LearningEntryContent(
    selectedTopic: String,
    onTopicSelect: (String) -> Unit,
    onStartQuiz: () -> Unit,
    onMyScore: () -> Unit,
    onLeaderboard: () -> Unit
) {
    Text("RMP Learning", style = MaterialTheme.typography.headlineMedium, color = MaterialTheme.colorScheme.primary)
    Text("Practice with quiz questions and see your rank.", style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
    Spacer(Modifier.height(Spacing.space16))
    Text("Topic", style = MaterialTheme.typography.labelLarge)
    Spacer(Modifier.height(Spacing.space8))
    FlowRow(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.spacedBy(8.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        TOPICS.forEach { topic ->
            FilterChip(
                selected = topic == selectedTopic,
                onClick = { onTopicSelect(topic) },
                label = {
                    Text(if (topic == "general") "General" else topic.replaceFirstChar { it.uppercase() })
                }
            )
        }
    }
    Spacer(Modifier.height(Spacing.space24))
    Button(onClick = onStartQuiz, modifier = Modifier.fillMaxWidth()) {
        Text("Start quiz")
    }
    Spacer(Modifier.height(Spacing.space12))
    OutlinedButton(onClick = onMyScore, modifier = Modifier.fillMaxWidth()) {
        Text("My score")
    }
    Spacer(Modifier.height(Spacing.space8))
    OutlinedButton(onClick = onLeaderboard, modifier = Modifier.fillMaxWidth()) {
        Text("Leaderboard")
    }
}

@Composable
private fun LearningQuestionContent(
    question: String,
    userAnswer: String,
    onAnswerChange: (String) -> Unit,
    onSubmit: () -> Unit,
    loading: Boolean,
    onBack: () -> Unit
) {
    Text("Question", style = MaterialTheme.typography.titleLarge)
    Spacer(Modifier.height(Spacing.space8))
    Card(colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)) {
        Text(question, style = MaterialTheme.typography.bodyLarge, modifier = Modifier.padding(Spacing.space16))
    }
    Spacer(Modifier.height(Spacing.space16))
    OutlinedTextField(
        value = userAnswer,
        onValueChange = onAnswerChange,
        label = { Text("Your answer") },
        modifier = Modifier.fillMaxWidth(),
        minLines = 3,
        enabled = !loading
    )
    Spacer(Modifier.height(Spacing.space16))
    if (loading) {
        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.Center) {
            CircularProgressIndicator()
        }
    } else {
        Button(onClick = onSubmit, modifier = Modifier.fillMaxWidth(), enabled = userAnswer.isNotBlank()) {
            Text("Submit answer")
        }
    }
    Spacer(Modifier.height(Spacing.space8))
    TextButton(onClick = onBack) { Text("Cancel") }
}

@Composable
private fun LearningResultContent(
    scoreResult: LearningScoreResult?,
    onNextQuestion: () -> Unit,
    onBack: () -> Unit
) {
    Text("Result", style = MaterialTheme.typography.titleLarge)
    Spacer(Modifier.height(Spacing.space16))
    if (scoreResult != null) {
        Card(colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.primaryContainer)) {
            Column(Modifier.padding(Spacing.space16)) {
                Text("Points: ${scoreResult.points}/10", style = MaterialTheme.typography.headlineSmall)
                if (scoreResult.feedback.isNotBlank()) {
                    Spacer(Modifier.height(Spacing.space8))
                    Text(scoreResult.feedback, style = MaterialTheme.typography.bodyMedium)
                }
            }
        }
    }
    Spacer(Modifier.height(Spacing.space24))
    Button(onClick = onNextQuestion, modifier = Modifier.fillMaxWidth()) {
        Text("Next question")
    }
    Spacer(Modifier.height(Spacing.space8))
    TextButton(onClick = onBack) { Text("Back to Learning") }
}

@Composable
private fun LearningMyScoreContent(
    myScore: LearningMyScore?,
    loading: Boolean,
    onBack: () -> Unit
) {
    Text("My score", style = MaterialTheme.typography.titleLarge)
    Spacer(Modifier.height(Spacing.space16))
    if (loading) {
        CircularProgressIndicator()
    } else if (myScore != null) {
        Card(colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)) {
            Column(Modifier.padding(Spacing.space16)) {
                Text("Total points: ${myScore.totalPoints}", style = MaterialTheme.typography.titleMedium)
                Text(
                    if (myScore.rank != null) "Rank: #${myScore.rank}" else "You haven't answered any questions yet.",
                    style = MaterialTheme.typography.bodyLarge
                )
            }
        }
    }
    Spacer(Modifier.height(Spacing.space16))
    TextButton(onClick = onBack) { Text("Back") }
}

@Composable
private fun LearningLeaderboardContent(
    leaderboard: List<LeaderboardEntry>,
    loading: Boolean,
    onBack: () -> Unit
) {
    Text("Leaderboard", style = MaterialTheme.typography.titleLarge)
    Spacer(Modifier.height(Spacing.space16))
    if (loading) {
        CircularProgressIndicator()
    } else {
        leaderboard.forEach { entry ->
            Card(
                modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
            ) {
                Row(
                    Modifier.fillMaxWidth().padding(Spacing.space16),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Text("#${entry.rank}", style = MaterialTheme.typography.titleMedium)
                    Text("${entry.totalPoints} pts", style = MaterialTheme.typography.bodyLarge)
                }
            }
        }
        if (leaderboard.isEmpty()) {
            Text("No entries yet.", style = MaterialTheme.typography.bodyMedium)
        }
    }
    Spacer(Modifier.height(Spacing.space16))
    TextButton(onClick = onBack) { Text("Back") }
}
