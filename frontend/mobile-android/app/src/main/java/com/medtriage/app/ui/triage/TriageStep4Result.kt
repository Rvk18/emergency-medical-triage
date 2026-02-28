package com.medtriage.app.ui.triage

import androidx.compose.foundation.background
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
import androidx.compose.ui.graphics.Color
import com.medtriage.app.data.triage.SeverityLevel
import com.medtriage.app.data.triage.TriageResult
import com.medtriage.app.ui.theme.SeverityCritical
import com.medtriage.app.ui.theme.SeverityHigh
import com.medtriage.app.ui.theme.SeverityLow
import com.medtriage.app.ui.theme.SeverityMedium
import com.medtriage.app.ui.theme.Spacing

private fun severityColor(level: SeverityLevel): Color = when (level) {
    SeverityLevel.CRITICAL -> SeverityCritical
    SeverityLevel.HIGH -> SeverityHigh
    SeverityLevel.MEDIUM -> SeverityMedium
    SeverityLevel.LOW -> SeverityLow
}

@Composable
fun TriageStep4Result(
    result: TriageResult,
    onProceedToReport: () -> Unit,
    onOverride: () -> Unit
) {
    val displaySeverity = if (result.confidencePercent < 85) SeverityLevel.HIGH else result.severity
    val showFlagForReview = result.flaggedForReview || result.confidencePercent < 85

    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(Spacing.space16)
            .verticalScroll(rememberScrollState())
    ) {
        Text("Step 4 of 4 — Result", style = MaterialTheme.typography.titleMedium)
        Spacer(Modifier.height(Spacing.space16))
        Text(
            text = "Severity: $displaySeverity",
            style = MaterialTheme.typography.titleLarge,
            modifier = Modifier
                .fillMaxWidth()
                .padding(Spacing.space8)
                .background(severityColor(displaySeverity).copy(alpha = 0.2f))
                .padding(Spacing.space8)
        )
        if (showFlagForReview) {
            Text(
                "Treat as HIGH priority — Flag for doctor review",
                style = MaterialTheme.typography.bodyMedium,
                color = SeverityHigh,
                modifier = Modifier.padding(vertical = Spacing.space8)
            )
        }
        Text("Confidence: ${result.confidencePercent}%", style = MaterialTheme.typography.bodyLarge)
        Spacer(Modifier.height(Spacing.space8))
        Text("Recommended actions:", style = MaterialTheme.typography.labelLarge)
        result.recommendedActions.forEach { Text("• $it", style = MaterialTheme.typography.bodyMedium) }
        Spacer(Modifier.height(Spacing.space16))
        Text("Safety disclaimers:", style = MaterialTheme.typography.labelLarge)
        result.safetyDisclaimers.forEach { Text(it, style = MaterialTheme.typography.bodySmall) }
        Spacer(Modifier.height(Spacing.space24))
        androidx.compose.material3.OutlinedButton(onClick = onOverride, modifier = Modifier.fillMaxWidth()) {
            Text("Override")
        }
        Spacer(Modifier.height(Spacing.space8))
        androidx.compose.material3.Button(onClick = onProceedToReport, modifier = Modifier.fillMaxWidth()) {
            Text("Proceed to Report")
        }
    }
}
