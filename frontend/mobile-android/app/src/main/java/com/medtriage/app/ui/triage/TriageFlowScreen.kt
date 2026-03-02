package com.medtriage.app.ui.triage

import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.hilt.navigation.compose.hiltViewModel
import com.medtriage.app.ui.theme.Spacing

@Composable
fun TriageFlowScreen(
    viewModel: TriageViewModel = hiltViewModel(),
    onProceedToHospitalMatching: () -> Unit
) {
    val state by viewModel.state.collectAsState()

    when {
        state.result != null && state.currentStep == 5 -> {
            TriageReportScreen(
                result = state.result!!,
                onProceedToHospitalMatching = onProceedToHospitalMatching
            )
        }
        state.result != null && state.currentStep == 4 -> {
            TriageStep4Result(
                result = state.result!!,
                onProceedToReport = { viewModel.nextStep() },
                onOverride = { /* TODO: override flow */ }
            )
        }
        state.currentStep == 0 -> {
            Box(Modifier.fillMaxSize().padding(Spacing.screenHorizontal), contentAlignment = Alignment.Center) {
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Text("Start new triage assessment", style = androidx.compose.material3.MaterialTheme.typography.headlineSmall)
                    Text("Capture patient info, symptoms, and vitals for AI assessment", style = androidx.compose.material3.MaterialTheme.typography.bodyMedium, modifier = Modifier.padding(top = Spacing.space8))
                    Spacer(modifier = Modifier.height(Spacing.sectionGap))
                    Button(onClick = { viewModel.goToStep(1) }) { Text("Start") }
                }
            }
        }
        state.currentStep == 1 -> TriageStep1PatientInfo(
            patientInfo = state.patientInfo,
            onUpdate = viewModel::updatePatientInfo,
            onNext = viewModel::nextStep
        )
        state.currentStep == 2 -> TriageStep2Symptoms(
            symptoms = state.symptoms,
            onUpdate = viewModel::updateSymptoms,
            onNext = viewModel::nextStep
        )
        state.currentStep == 3 -> TriageStep3Vitals(
            vitals = state.vitals,
            onUpdate = viewModel::updateVitals,
            onAssess = viewModel::runAssessment,
            isAssessing = state.isAssessing
        )
        else -> {
            Box(Modifier.fillMaxSize().padding(Spacing.screenHorizontal), contentAlignment = Alignment.Center) {
                Text("Loading…", style = androidx.compose.material3.MaterialTheme.typography.bodyLarge)
            }
        }
    }
}
