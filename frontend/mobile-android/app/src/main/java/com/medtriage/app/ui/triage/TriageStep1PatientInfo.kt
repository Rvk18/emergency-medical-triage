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
import com.medtriage.app.data.triage.PatientInfo
import com.medtriage.app.ui.components.TriageStepBar
import com.medtriage.app.ui.theme.Spacing

import com.medtriage.app.ui.utils.Translator

@Composable
fun TriageStep1PatientInfo(
    patientInfo: PatientInfo,
    selectedLangCode: String = "en",
    onUpdate: (PatientInfo) -> Unit,
    onNext: () -> Unit,
    onBack: () -> Unit
) {
    var age by mutableStateOf(patientInfo.age?.toString() ?: "")
    var gender by mutableStateOf(patientInfo.gender ?: "")
    var history by mutableStateOf(patientInfo.medicalHistory ?: "")
    var allergies by mutableStateOf(patientInfo.allergies ?: "")

    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = Spacing.screenHorizontal)
            .verticalScroll(rememberScrollState())
    ) {
        TriageStepBar(stepIndicator = "${Translator.t("Step", selectedLangCode)} 1 ${Translator.t("of", selectedLangCode)} 4", onBack = onBack)
        Spacer(Modifier.height(Spacing.space8))
        Text(Translator.t("Patient Information", selectedLangCode), style = androidx.compose.material3.MaterialTheme.typography.headlineSmall)
        Spacer(Modifier.height(Spacing.sectionGap))
        OutlinedTextField(
            value = age,
            onValueChange = { age = it; onUpdate(patientInfo.copy(age = it.toIntOrNull())) },
            label = { Text(Translator.t("Age", selectedLangCode)) },
            modifier = Modifier.fillMaxWidth()
        )
        Spacer(Modifier.height(Spacing.space8))
        OutlinedTextField(
            value = gender,
            onValueChange = { gender = it; onUpdate(patientInfo.copy(gender = it.ifBlank { null })) },
            label = { Text(Translator.t("Gender", selectedLangCode)) },
            modifier = Modifier.fillMaxWidth()
        )
        Spacer(Modifier.height(Spacing.space8))
        Text(Translator.t("Location: GPS auto-detect", selectedLangCode), style = androidx.compose.material3.MaterialTheme.typography.bodySmall)
        Spacer(Modifier.height(Spacing.space8))
        OutlinedTextField(
            value = history,
            onValueChange = { history = it; onUpdate(patientInfo.copy(medicalHistory = it.ifBlank { null })) },
            label = { Text(Translator.t("Medical history (optional)", selectedLangCode)) },
            modifier = Modifier.fillMaxWidth(),
            minLines = 2
        )
        Spacer(Modifier.height(Spacing.space8))
        OutlinedTextField(
            value = allergies,
            onValueChange = { allergies = it; onUpdate(patientInfo.copy(allergies = it.ifBlank { null })) },
            label = { Text(Translator.t("Allergies (optional)", selectedLangCode)) },
            modifier = Modifier.fillMaxWidth()
        )
        Spacer(Modifier.height(Spacing.space24))
        Button(onClick = onNext, modifier = Modifier.fillMaxWidth()) { Text(Translator.t("Next", selectedLangCode)) }
    }
}
