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

import com.medtriage.app.ui.utils.Translator

@Composable
fun TriageFlowScreen(
    viewModel: TriageViewModel = hiltViewModel(),
    selectedLangCode: String = "en",
    onProceedToHospitalMatching: () -> Unit
) {
    val state by viewModel.state.collectAsState()

    when {
        state.result != null && state.currentStep == 5 -> {
            TriageReportScreen(
                result = state.result!!,
                selectedLangCode = selectedLangCode,
                onProceedToHospitalMatching = {
                    viewModel.saveResultForHospitals()
                    onProceedToHospitalMatching()
                },
                onBack = { viewModel.goToStep(4) }
            )
        }
        state.result != null && state.currentStep == 4 -> {
            TriageStep4Result(
                result = state.result!!,
                selectedLangCode = selectedLangCode,
                onProceedToReport = { viewModel.nextStep() },
                onOverride = { /* TODO: override flow */ },
                onBack = { viewModel.goToStep(3) }
            )
        }
        state.currentStep == 0 -> {
            Box(Modifier.fillMaxSize().padding(Spacing.screenHorizontal), contentAlignment = Alignment.Center) {
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Text(Translator.t("Start new triage assessment", selectedLangCode), style = androidx.compose.material3.MaterialTheme.typography.headlineSmall)
                    Text(Translator.t("Capture patient info, symptoms, and vitals for AI assessment", selectedLangCode), style = androidx.compose.material3.MaterialTheme.typography.bodyMedium, modifier = Modifier.padding(top = Spacing.space8))
                    Spacer(modifier = Modifier.height(Spacing.sectionGap))
                    Button(onClick = { viewModel.goToStep(1) }) { Text(Translator.t("Start", selectedLangCode)) }
                }
            }
        }
        state.currentStep == 1 -> TriageStep1PatientInfo(
            patientInfo = state.patientInfo,
            selectedLangCode = selectedLangCode,
            onUpdate = viewModel::updatePatientInfo,
            onNext = viewModel::nextStep,
            onBack = { viewModel.goToStep(0) }
        )
        state.currentStep == 2 -> TriageStep2Symptoms(
            symptoms = state.symptoms,
            selectedLangCode = selectedLangCode,
            onUpdate = viewModel::updateSymptoms,
            onNext = viewModel::nextStep,
            onBack = { viewModel.goToStep(1) }
        )
        state.currentStep == 3 -> TriageStep3Vitals(
            vitals = state.vitals,
            selectedLangCode = selectedLangCode,
            onUpdate = viewModel::updateVitals,
            onAssess = viewModel::runAssessment,
            onBack = { viewModel.goToStep(2) },
            isAssessing = state.isAssessing,
            assessError = state.assessError
        )
        else -> {
            Box(Modifier.fillMaxSize().padding(Spacing.screenHorizontal), contentAlignment = Alignment.Center) {
                Text(Translator.t("Loading…", selectedLangCode), style = androidx.compose.material3.MaterialTheme.typography.bodyLarge)
            }
        }
    }
}
