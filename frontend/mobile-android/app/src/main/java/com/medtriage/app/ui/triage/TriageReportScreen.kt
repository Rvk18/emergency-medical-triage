package com.medtriage.app.ui.triage

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import com.medtriage.app.data.triage.TriageResult
import com.medtriage.app.ui.components.ConfidenceBar
import com.medtriage.app.ui.components.TriageStepBar
import com.medtriage.app.ui.components.SectionCard
import com.medtriage.app.ui.components.SeverityChip
import com.medtriage.app.ui.theme.Spacing

import com.medtriage.app.ui.utils.Translator

@Composable
fun TriageReportScreen(
    result: TriageResult,
    selectedLangCode: String = "en",
    onProceedToHospitalMatching: () -> Unit,
    onBack: () -> Unit
) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = Spacing.screenHorizontal)
            .verticalScroll(rememberScrollState())
    ) {
        TriageStepBar(stepIndicator = Translator.t("Report", selectedLangCode), onBack = onBack)
        Spacer(Modifier.height(Spacing.space8))
        Text(Translator.t("Triage Report", selectedLangCode), style = MaterialTheme.typography.headlineMedium, color = MaterialTheme.colorScheme.onSurface)
        Spacer(Modifier.height(Spacing.sectionGap))

        SectionCard(title = Translator.t("Summary", selectedLangCode)) {
            Text("ID: ${result.emergencyId}", style = MaterialTheme.typography.labelSmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
            Spacer(Modifier.height(Spacing.space12))
            SeverityChip(severity = result.severity, selectedLangCode = selectedLangCode, modifier = Modifier.padding(bottom = Spacing.space12))
            ConfidenceBar(confidencePercent = result.confidencePercent)
        }
        Spacer(Modifier.height(Spacing.space16))

        SectionCard(title = Translator.t("Recommended actions", selectedLangCode)) {
            result.recommendedActions.forEach { action ->
                Text("• $action", style = MaterialTheme.typography.bodyMedium, modifier = Modifier.padding(vertical = Spacing.space4))
            }
        }
        Spacer(Modifier.height(Spacing.sectionGap))

        Button(onClick = onProceedToHospitalMatching, modifier = Modifier.fillMaxWidth()) {
            Text(Translator.t("Proceed to Hospital Matching", selectedLangCode))
        }
        Spacer(Modifier.height(Spacing.space40))
    }
}
