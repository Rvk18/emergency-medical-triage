package com.medtriage.app.ui.hospitals

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
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
import com.medtriage.app.data.hospitals.HospitalMatch
import com.medtriage.app.data.hospitals.RouteStep
import com.medtriage.app.ui.theme.Spacing

@Composable
fun NavigationScreen(
    hospital: HospitalMatch,
    steps: List<RouteStep>,
    onGenerateHandoff: () -> Unit,
    onChangeHospital: () -> Unit
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(Spacing.space16)
    ) {
        Text("Navigation to ${hospital.name}", style = MaterialTheme.typography.titleLarge)
        Text("ETA: ${hospital.etaMinutes} min", style = MaterialTheme.typography.bodyLarge)
        Spacer(Modifier.height(Spacing.space16))
        Text("Turn-by-turn:", style = MaterialTheme.typography.labelLarge)
        Column(modifier = Modifier.verticalScroll(rememberScrollState())) {
            steps.forEachIndexed { i, step ->
                Text("${i + 1}. ${step.instruction}", style = MaterialTheme.typography.bodyMedium)
            }
        }
        Spacer(Modifier.height(Spacing.space24))
        Button(onClick = onChangeHospital, modifier = Modifier.fillMaxWidth()) { Text("Change hospital") }
        Spacer(Modifier.height(Spacing.space8))
        Button(onClick = onGenerateHandoff, modifier = Modifier.fillMaxWidth()) { Text("Generate Handoff Report") }
    }
}
