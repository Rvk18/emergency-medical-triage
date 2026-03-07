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

@Composable
fun TriageReportScreen(
    result: TriageResult,
    onProceedToHospitalMatching: () -> Unit,
    onBack: () -> Unit
) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = Spacing.screenHorizontal)
            .verticalScroll(rememberScrollState())
    ) {
        TriageStepBar(stepIndicator = "Report", onBack = onBack)
        Spacer(Modifier.height(Spacing.space8))
        Text("Triage Report", style = MaterialTheme.typography.headlineMedium, color = MaterialTheme.colorScheme.onSurface)
        Spacer(Modifier.height(Spacing.sectionGap))

        SectionCard(title = "Summary") {
            Text("ID: ${result.emergencyId}", style = MaterialTheme.typography.labelSmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
            Spacer(Modifier.height(Spacing.space12))
            SeverityChip(severity = result.severity, modifier = Modifier.padding(bottom = Spacing.space12))
            ConfidenceBar(confidencePercent = result.confidencePercent)
        }
        Spacer(Modifier.height(Spacing.space16))

        SectionCard(title = "Recommended actions") {
            result.recommendedActions.forEach { action ->
                Text("• $action", style = MaterialTheme.typography.bodyMedium, modifier = Modifier.padding(vertical = Spacing.space4))
            }
        }
        Spacer(Modifier.height(Spacing.sectionGap))

        Button(onClick = onProceedToHospitalMatching, modifier = Modifier.fillMaxWidth()) {
            Text("Proceed to Hospital Matching")
        }
        Spacer(Modifier.height(Spacing.space40))
    }
}
