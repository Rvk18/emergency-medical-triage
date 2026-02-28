package com.medtriage.app.ui.triage

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.medtriage.app.data.triage.PatientInfo
import com.medtriage.app.data.triage.SeverityLevel
import com.medtriage.app.data.triage.SymptomInput
import com.medtriage.app.data.triage.TriageRepository
import com.medtriage.app.data.triage.TriageResult
import com.medtriage.app.data.triage.VitalsInput
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.catch
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject

data class TriageWizardState(
    val currentStep: Int = 0,
    val patientInfo: PatientInfo = PatientInfo(),
    val symptoms: SymptomInput = SymptomInput(),
    val vitals: VitalsInput = VitalsInput(),
    val result: TriageResult? = null,
    val isAssessing: Boolean = false,
    val assessError: String? = null
)

@HiltViewModel
class TriageViewModel @Inject constructor(
    private val triageRepository: TriageRepository
) : ViewModel() {

    private val _state = MutableStateFlow(TriageWizardState())
    val state: StateFlow<TriageWizardState> = _state.asStateFlow()

    fun updatePatientInfo(patientInfo: PatientInfo) {
        _state.update { it.copy(patientInfo = patientInfo) }
    }

    fun updateSymptoms(symptoms: SymptomInput) {
        _state.update { it.copy(symptoms = symptoms) }
    }

    fun updateVitals(vitals: VitalsInput) {
        _state.update { it.copy(vitals = vitals) }
    }

    fun nextStep() {
        _state.update { it ->
            val next = when (it.currentStep) {
                1, 2, 3 -> it.currentStep + 1
                4 -> 5
                else -> it.currentStep
            }
            it.copy(currentStep = next)
        }
    }

    fun goToStep(step: Int) {
        _state.update { it.copy(currentStep = step.coerceIn(0, 5)) }
    }

    fun runAssessment() {
        viewModelScope.launch {
            _state.update { it.copy(isAssessing = true, assessError = null) }
            triageRepository.assess(
                _state.value.patientInfo,
                _state.value.symptoms,
                _state.value.vitals
            ).catch { e ->
                _state.update {
                    it.copy(isAssessing = false, assessError = e.message)
                }
            }.collect { result ->
                result.fold(
                    onSuccess = { triageResult ->
                        _state.update {
                            it.copy(
                                isAssessing = false,
                                currentStep = 4,
                                result = triageResult,
                                assessError = null
                            )
                        }
                    },
                    onFailure = { e ->
                        _state.update {
                            it.copy(isAssessing = false, assessError = e.message)
                        }
                    }
                )
            }
        }
    }

    fun resetWizard() {
        _state.value = TriageWizardState()
    }
}
