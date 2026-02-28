package com.medtriage.app.ui.dashboard

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.medtriage.app.data.rmp.LearningModule
import com.medtriage.app.ui.theme.Spacing

@Composable
fun LearningScreen(
    modules: List<LearningModule>,
    loading: Boolean,
    onBack: () -> Unit = {}
) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(Spacing.space16)
            .verticalScroll(rememberScrollState())
    ) {
        androidx.compose.material3.TextButton(onClick = onBack) {
            Text("← Back to Dashboard")
        }
        Text("Learning modules", style = MaterialTheme.typography.headlineMedium)
        Spacer(Modifier.height(Spacing.space16))
        if (loading) Text("Loading…")
        modules.forEach { m ->
            Card(
                modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp),
                elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
            ) {
                Column(Modifier.padding(Spacing.space16)) {
                    Text(m.title, style = MaterialTheme.typography.titleMedium)
                    LinearProgressIndicator(
                        progress = m.progressPercent / 100f,
                        modifier = Modifier.fillMaxWidth().padding(vertical = 8.dp)
                    )
                    Text(
                        if (m.completed) "Completed" else "${m.progressPercent}%",
                        style = MaterialTheme.typography.bodySmall
                    )
                }
            }
        }
    }
}
