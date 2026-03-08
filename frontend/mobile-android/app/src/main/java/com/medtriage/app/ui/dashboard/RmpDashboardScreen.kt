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
import com.medtriage.app.ui.utils.Translator
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
    selectedLangCode: String = "en",
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
            Translator.t("RMP Dashboard", selectedLangCode),
            style = MaterialTheme.typography.headlineMedium,
            color = MaterialTheme.colorScheme.primary
        )
        Text(
            Translator.t("Your competency and recent activity", selectedLangCode),
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
                    title = Translator.t("No profile", selectedLangCode),
                    description = Translator.t("Your profile could not be loaded. Pull to refresh or try again later.", selectedLangCode)
                )
            }
            else -> {
                val p = profile
                SectionCard(title = Translator.t("Profile", selectedLangCode)) {
                    Text("${Translator.t("Competency", selectedLangCode)}: ${p.competencyScore}%", style = MaterialTheme.typography.titleSmall)
                    Text("${Translator.t("Level", selectedLangCode)}: ${p.levelBadge}", style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    Text("${Translator.t("Cases", selectedLangCode)}: ${p.casesCompleted} • ${Translator.t("Success", selectedLangCode)}: ${p.successRatePercent}%", style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                }
                Spacer(Modifier.height(Spacing.space16))
                SectionCard(title = Translator.t("Recent cases", selectedLangCode)) {
                    if (p.recentCases.isEmpty()) {
                        EmptyState(
                            title = Translator.t("No recent cases", selectedLangCode),
                            description = Translator.t("Completed triage cases will appear here.", selectedLangCode),
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
                    Text(Translator.t("Start Triage", selectedLangCode))
                }
                Spacer(Modifier.height(Spacing.space12))
                androidx.compose.material3.OutlinedButton(onClick = onShowLearning, modifier = Modifier.fillMaxWidth()) {
                    Text(Translator.t("Learning modules", selectedLangCode))
                }
                Spacer(Modifier.height(Spacing.space40))
            }
        }
    }
}
