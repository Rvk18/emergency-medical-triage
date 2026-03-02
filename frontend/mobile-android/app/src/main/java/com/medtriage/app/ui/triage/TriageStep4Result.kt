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
import com.medtriage.app.ui.theme.Spacing

@Composable
fun TriageStep4Result(
    result: TriageResult,
    onProceedToReport: () -> Unit,
    onOverride: () -> Unit
) {
    var showOverrideDialog by remember { mutableStateOf(false) }
    val displaySeverity = if (result.confidencePercent < 85) SeverityLevel.HIGH else result.severity
    val showFlagForReview = result.flaggedForReview || result.confidencePercent < 85

    if (showOverrideDialog) {
        ConfirmationDialog(
            title = "Override severity",
            body = "Changing the AI assessment will be logged for audit. Confirm override?",
            confirmLabel = "Override",
            dismissLabel = "Cancel",
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
            .padding(Spacing.screenHorizontal)
            .verticalScroll(rememberScrollState())
    ) {
        if (result.severity == SeverityLevel.CRITICAL) {
            CriticalBanner(message = "CRITICAL — Immediate transport. Do not delay.")
            Spacer(Modifier.height(Spacing.space16))
        }
        Text("Step 4 of 4 — Result", style = MaterialTheme.typography.headlineSmall, color = MaterialTheme.colorScheme.onSurface)
        Spacer(Modifier.height(Spacing.sectionGap))

        SectionCard(title = "Assessment") {
            SeverityChip(severity = displaySeverity, modifier = Modifier.padding(bottom = Spacing.space12))
            ConfidenceBar(confidencePercent = result.confidencePercent)
        }
        if (showFlagForReview) {
            Spacer(Modifier.height(Spacing.space16))
            SectionCard(
                title = "Flag for doctor review",
                variant = SectionCardVariant.Warning
            ) {
                Text(
                    "Treat as HIGH priority. Low confidence — recommend doctor review.",
                    style = MaterialTheme.typography.bodyMedium
                )
            }
        }
        Spacer(Modifier.height(Spacing.space16))

        SectionCard(title = "Recommended actions") {
            result.recommendedActions.forEach { action ->
                Text("• $action", style = MaterialTheme.typography.bodyMedium, modifier = Modifier.padding(vertical = Spacing.space4))
            }
        }
        Spacer(Modifier.height(Spacing.space16))

        SectionCard(title = "Safety notice") {
            result.safetyDisclaimers.forEach { Text(it, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant) }
        }
        Spacer(Modifier.height(Spacing.sectionGap))

        OutlinedButton(onClick = { showOverrideDialog = true }, modifier = Modifier.fillMaxWidth()) {
            Text("Override")
        }
        Spacer(Modifier.height(Spacing.space12))
        Button(onClick = onProceedToReport, modifier = Modifier.fillMaxWidth()) {
            Text("Proceed to Report")
        }
        Spacer(Modifier.height(Spacing.space40))
    }
}
