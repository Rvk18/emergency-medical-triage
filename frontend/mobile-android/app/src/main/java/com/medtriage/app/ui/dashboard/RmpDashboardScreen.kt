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
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.medtriage.app.data.rmp.RmpProfile
import com.medtriage.app.ui.theme.Spacing

@Composable
fun RmpDashboardScreen(
    profile: RmpProfile?,
    loading: Boolean,
    onStartTriage: () -> Unit,
    onShowLearning: () -> Unit = {}
) {
    val scroll = rememberScrollState()
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(Spacing.space16)
            .verticalScroll(scroll)
    ) {
        Text("RMP Dashboard", style = MaterialTheme.typography.headlineMedium)
        Spacer(Modifier.height(Spacing.space16))
        if (loading) Text("Loading…")
        profile?.let { p ->
            Card(modifier = Modifier.fillMaxWidth(), elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)) {
                Column(Modifier.padding(Spacing.space16)) {
                    Text("Competency: ${p.competencyScore}%", style = MaterialTheme.typography.titleMedium)
                    Text("Level: ${p.levelBadge}", style = MaterialTheme.typography.bodyMedium)
                    Text("Cases: ${p.casesCompleted} • Success: ${p.successRatePercent}%", style = MaterialTheme.typography.bodySmall)
                }
            }
            Spacer(Modifier.height(Spacing.space16))
            Text("Recent cases", style = MaterialTheme.typography.labelLarge)
            p.recentCases.forEach { c ->
                Text("• ${c.summary} (${c.severity})", style = MaterialTheme.typography.bodyMedium)
            }
            Spacer(Modifier.height(Spacing.space24))
            androidx.compose.material3.Button(onClick = onStartTriage, modifier = Modifier.fillMaxWidth()) {
                Text("Start Triage")
            }
            Spacer(Modifier.height(Spacing.space8))
            androidx.compose.material3.OutlinedButton(onClick = onShowLearning, modifier = Modifier.fillMaxWidth()) {
                Text("Learning modules")
            }
        }
    }
}
