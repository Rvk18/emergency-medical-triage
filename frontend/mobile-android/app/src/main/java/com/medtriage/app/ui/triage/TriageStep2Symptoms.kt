package com.medtriage.app.ui.triage

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import com.medtriage.app.data.triage.SymptomInput
import com.medtriage.app.ui.theme.Spacing

@Composable
fun TriageStep2Symptoms(
    symptoms: SymptomInput,
    onUpdate: (SymptomInput) -> Unit,
    onNext: () -> Unit
) {
    var freeText by mutableStateOf(symptoms.freeText)
    var duration by mutableStateOf(symptoms.durationMinutes?.toString() ?: "")
    var severity by mutableStateOf(symptoms.patientReportedSeverity ?: "")

    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(Spacing.space16)
            .verticalScroll(rememberScrollState())
    ) {
        Text("Step 2 of 4 — Symptoms", style = androidx.compose.material3.MaterialTheme.typography.titleMedium)
        Spacer(Modifier.height(Spacing.space16))
        OutlinedTextField(
            value = freeText,
            onValueChange = { freeText = it; onUpdate(symptoms.copy(freeText = it)) },
            label = { Text("Describe symptoms") },
            modifier = Modifier.fillMaxWidth(),
            minLines = 3
        )
        Spacer(Modifier.height(Spacing.space8))
        OutlinedTextField(
            value = duration,
            onValueChange = { duration = it; onUpdate(symptoms.copy(durationMinutes = it.toIntOrNull())) },
            label = { Text("Duration (minutes)") },
            modifier = Modifier.fillMaxWidth()
        )
        Spacer(Modifier.height(Spacing.space8))
        OutlinedTextField(
            value = severity,
            onValueChange = { severity = it; onUpdate(symptoms.copy(patientReportedSeverity = it.ifBlank { null })) },
            label = { Text("Patient-reported severity") },
            modifier = Modifier.fillMaxWidth()
        )
        Spacer(Modifier.height(Spacing.space24))
        Button(onClick = onNext, modifier = Modifier.fillMaxWidth()) { Text("Next") }
    }
}
