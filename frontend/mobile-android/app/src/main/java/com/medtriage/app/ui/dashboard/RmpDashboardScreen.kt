package com.medtriage.app.ui.dashboard

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import com.medtriage.app.data.rmp.RmpProfile
import com.medtriage.app.ui.components.EmptyState
import com.medtriage.app.ui.components.SectionCard
import com.medtriage.app.ui.components.SkeletonCard
import com.medtriage.app.ui.theme.Spacing

@Composable
fun RmpDashboardScreen(
    profile: RmpProfile?,
    loading: Boolean,
    onStartTriage: () -> Unit,
    onShowLearning: () -> Unit = {}
) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(Spacing.screenHorizontal)
            .verticalScroll(rememberScrollState())
    ) {
        Text(
            "RMP Dashboard",
            style = MaterialTheme.typography.headlineMedium,
            color = MaterialTheme.colorScheme.primary
        )
        Text(
            "Your competency and recent activity",
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            modifier = Modifier.padding(top = Spacing.space4)
        )
        Spacer(Modifier.height(Spacing.sectionGap))
        when {
            loading -> {
                SkeletonCard(modifier = Modifier.padding(bottom = Spacing.space16))
                SkeletonCard()
            }
            profile == null -> {
                EmptyState(
                    title = "No profile",
                    description = "Your profile could not be loaded. Pull to refresh or try again later."
                )
            }
            else -> {
                val p = profile
                SectionCard(title = "Profile") {
                    Text("Competency: ${p.competencyScore}%", style = MaterialTheme.typography.titleSmall)
                    Text("Level: ${p.levelBadge}", style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    Text("Cases: ${p.casesCompleted} • Success: ${p.successRatePercent}%", style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                }
                Spacer(Modifier.height(Spacing.space16))
                SectionCard(title = "Recent cases") {
                    if (p.recentCases.isEmpty()) {
                        EmptyState(
                            title = "No recent cases",
                            description = "Completed triage cases will appear here.",
                            modifier = Modifier.padding(vertical = Spacing.space16)
                        )
                    } else {
                        p.recentCases.forEach { c ->
                            Text("• ${c.summary} (${c.severity})", style = MaterialTheme.typography.bodyMedium, modifier = Modifier.padding(vertical = Spacing.space4))
                        }
                    }
                }
                Spacer(Modifier.height(Spacing.sectionGap))
                androidx.compose.material3.FilledTonalButton(onClick = onStartTriage, modifier = Modifier.fillMaxWidth()) {
                    Text("Start Triage")
                }
                Spacer(Modifier.height(Spacing.space12))
                androidx.compose.material3.OutlinedButton(onClick = onShowLearning, modifier = Modifier.fillMaxWidth()) {
                    Text("Learning modules")
                }
                Spacer(Modifier.height(Spacing.space40))
            }
        }
    }
}
