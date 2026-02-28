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
import com.medtriage.app.data.triage.VitalsInput
import com.medtriage.app.ui.theme.Spacing

@Composable
fun TriageStep3Vitals(
    vitals: VitalsInput,
    onUpdate: (VitalsInput) -> Unit,
    onAssess: () -> Unit,
    isAssessing: Boolean = false
) {
    var hr by mutableStateOf(vitals.heartRateBpm?.toString() ?: "")
    var bpSys by mutableStateOf(vitals.bloodPressureSystolic?.toString() ?: "")
    var bpDia by mutableStateOf(vitals.bloodPressureDiastolic?.toString() ?: "")
    var temp by mutableStateOf(vitals.temperatureCelsius?.toString() ?: "")
    var spo2 by mutableStateOf(vitals.spo2Percent?.toString() ?: "")
    var respRate by mutableStateOf(vitals.respiratoryRatePerMin?.toString() ?: "")
    var avpu by mutableStateOf(vitals.consciousnessAvpu ?: "")

    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(Spacing.space16)
            .verticalScroll(rememberScrollState())
    ) {
        Text("Step 3 of 4 — Vitals", style = androidx.compose.material3.MaterialTheme.typography.titleMedium)
        Spacer(Modifier.height(Spacing.space16))
        OutlinedTextField(value = hr, onValueChange = { hr = it; onUpdate(vitals.copy(heartRateBpm = it.toIntOrNull())) }, label = { Text("Heart rate (bpm)") }, modifier = Modifier.fillMaxWidth())
        Spacer(Modifier.height(Spacing.space8))
        OutlinedTextField(value = bpSys, onValueChange = { bpSys = it; onUpdate(vitals.copy(bloodPressureSystolic = it.toIntOrNull())) }, label = { Text("BP systolic") }, modifier = Modifier.fillMaxWidth())
        OutlinedTextField(value = bpDia, onValueChange = { bpDia = it; onUpdate(vitals.copy(bloodPressureDiastolic = it.toIntOrNull())) }, label = { Text("BP diastolic") }, modifier = Modifier.fillMaxWidth())
        Spacer(Modifier.height(Spacing.space8))
        OutlinedTextField(value = temp, onValueChange = { temp = it; onUpdate(vitals.copy(temperatureCelsius = it.toFloatOrNull())) }, label = { Text("Temperature (°C)") }, modifier = Modifier.fillMaxWidth())
        OutlinedTextField(value = spo2, onValueChange = { spo2 = it; onUpdate(vitals.copy(spo2Percent = it.toIntOrNull())) }, label = { Text("SpO2 (%)") }, modifier = Modifier.fillMaxWidth())
        OutlinedTextField(value = respRate, onValueChange = { respRate = it; onUpdate(vitals.copy(respiratoryRatePerMin = it.toIntOrNull())) }, label = { Text("Respiratory rate") }, modifier = Modifier.fillMaxWidth())
        OutlinedTextField(value = avpu, onValueChange = { avpu = it; onUpdate(vitals.copy(consciousnessAvpu = it.ifBlank { null })) }, label = { Text("Consciousness (AVPU)") }, modifier = Modifier.fillMaxWidth())
        Spacer(Modifier.height(Spacing.space24))
        Button(onClick = onAssess, modifier = Modifier.fillMaxWidth(), enabled = !isAssessing) {
            Text(if (isAssessing) "Assessing…" else "Assess")
        }
    }
}
