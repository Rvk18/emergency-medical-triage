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
import com.medtriage.app.ui.theme.Spacing

@Composable
fun TriageReportScreen(
    result: TriageResult,
    onProceedToHospitalMatching: () -> Unit
) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(Spacing.space16)
            .verticalScroll(rememberScrollState())
    ) {
        Text("Triage Report", style = MaterialTheme.typography.headlineMedium)
        Spacer(Modifier.height(Spacing.space16))
        Text("Emergency ID: ${result.emergencyId}", style = MaterialTheme.typography.bodyMedium)
        Text("Severity: ${result.severity}", style = MaterialTheme.typography.bodyLarge)
        Text("Confidence: ${result.confidencePercent}%", style = MaterialTheme.typography.bodyMedium)
        Spacer(Modifier.height(Spacing.space8))
        Text("Recommended actions:", style = MaterialTheme.typography.labelLarge)
        result.recommendedActions.forEach { Text("• $it", style = MaterialTheme.typography.bodyMedium) }
        Spacer(Modifier.height(Spacing.space24))
        Button(onClick = onProceedToHospitalMatching, modifier = Modifier.fillMaxWidth()) {
            Text("Proceed to Hospital Matching")
        }
    }
}
