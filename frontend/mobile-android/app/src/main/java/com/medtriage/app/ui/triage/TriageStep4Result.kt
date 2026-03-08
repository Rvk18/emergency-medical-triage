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
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import com.medtriage.app.data.triage.SeverityLevel
import com.medtriage.app.data.triage.TriageResult
import com.medtriage.app.ui.components.ConfidenceBar
import com.medtriage.app.ui.components.ConfirmationDialog
import com.medtriage.app.ui.components.CriticalBanner
import com.medtriage.app.ui.components.SectionCard
import com.medtriage.app.ui.components.SectionCardVariant
import com.medtriage.app.ui.components.SeverityChip
import com.medtriage.app.ui.components.TriageStepBar
import com.medtriage.app.ui.theme.Spacing

import com.medtriage.app.ui.utils.Translator

@Composable
fun TriageStep4Result(
    result: TriageResult,
    selectedLangCode: String = "en",
    onProceedToReport: () -> Unit,
    onOverride: () -> Unit,
    onBack: () -> Unit
) {
    var showOverrideDialog by remember { mutableStateOf(false) }
    val displaySeverity = if (result.confidencePercent < 85) SeverityLevel.HIGH else result.severity
    val showFlagForReview = result.flaggedForReview || result.confidencePercent < 85

    if (showOverrideDialog) {
        ConfirmationDialog(
            title = Translator.t("Override severity", selectedLangCode),
            body = Translator.t("Changing the AI assessment will be logged for audit. Confirm override?", selectedLangCode),
            confirmLabel = Translator.t("Override", selectedLangCode),
            dismissLabel = Translator.t("Cancel", selectedLangCode),
            onConfirm = {
                showOverrideDialog = false
                onOverride()
            },
            onDismiss = { showOverrideDialog = false }
        )
    }

    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = Spacing.screenHorizontal)
            .verticalScroll(rememberScrollState())
    ) {
        TriageStepBar(stepIndicator = "${Translator.t("Step", selectedLangCode)} 4 ${Translator.t("of", selectedLangCode)} 4", onBack = onBack)
        Spacer(Modifier.height(Spacing.space8))
        if (result.severity == SeverityLevel.CRITICAL) {
            CriticalBanner(message = Translator.t("CRITICAL — Immediate transport. Do not delay.", selectedLangCode))
            Spacer(Modifier.height(Spacing.space16))
        }
        Text(Translator.t("Result", selectedLangCode), style = MaterialTheme.typography.headlineSmall, color = MaterialTheme.colorScheme.onSurface)
        Spacer(Modifier.height(Spacing.sectionGap))

        SectionCard(title = Translator.t("Assessment", selectedLangCode)) {
            SeverityChip(severity = displaySeverity, selectedLangCode = selectedLangCode, modifier = Modifier.padding(bottom = Spacing.space12))
            ConfidenceBar(confidencePercent = result.confidencePercent)
        }
        if (showFlagForReview) {
            Spacer(Modifier.height(Spacing.space16))
            SectionCard(
                title = Translator.t("Flag for doctor review", selectedLangCode),
                variant = SectionCardVariant.Warning
            ) {
                Text(
                    Translator.t("Treat as HIGH priority. Low confidence — recommend doctor review.", selectedLangCode),
                    style = MaterialTheme.typography.bodyMedium
                )
            }
        }
        Spacer(Modifier.height(Spacing.space16))

        SectionCard(title = Translator.t("Recommended actions", selectedLangCode)) {
            result.recommendedActions.forEach { action ->
                // Note: action strings from AI might be in English unless AI is prompted to translate.
                // For hackathon, we keep the dynamic AI output as is or wrap it if we have fixed patterns.
                Text("• $action", style = MaterialTheme.typography.bodyMedium, modifier = Modifier.padding(vertical = Spacing.space4))
            }
        }
        Spacer(Modifier.height(Spacing.space16))

        SectionCard(title = Translator.t("Safety notice", selectedLangCode)) {
            result.safetyDisclaimers.forEach { Text(it, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant) }
        }
        Spacer(Modifier.height(Spacing.sectionGap))

        OutlinedButton(onClick = { showOverrideDialog = true }, modifier = Modifier.fillMaxWidth()) {
            Text(Translator.t("Override", selectedLangCode))
        }
        Spacer(Modifier.height(Spacing.space12))
        Button(onClick = onProceedToReport, modifier = Modifier.fillMaxWidth()) {
            Text(Translator.t("Proceed to Report", selectedLangCode))
        }
        Spacer(Modifier.height(Spacing.space40))
    }
}
