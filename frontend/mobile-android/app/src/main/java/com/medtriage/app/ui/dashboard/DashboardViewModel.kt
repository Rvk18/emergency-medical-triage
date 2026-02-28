package com.medtriage.app.ui.dashboard

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.medtriage.app.data.rmp.GuidanceStep
import com.medtriage.app.data.rmp.LearningModule
import com.medtriage.app.data.rmp.RmpProfile
import com.medtriage.app.data.rmp.RmpRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject

data class DashboardUiState(
    val profile: RmpProfile? = null,
    val profileLoading: Boolean = true,
    val modules: List<LearningModule> = emptyList(),
    val modulesLoading: Boolean = false,
    val guidanceSteps: List<GuidanceStep>? = null,
    val showGuidance: Boolean = false,
    val showLearning: Boolean = false
)

@HiltViewModel
class DashboardViewModel @Inject constructor(
    private val rmpRepository: RmpRepository
) : ViewModel() {

    private val _state = MutableStateFlow(DashboardUiState())
    val state: StateFlow<DashboardUiState> = _state.asStateFlow()

    init {
        loadProfile()
    }

    fun loadProfile() {
        viewModelScope.launch {
            _state.update { it.copy(profileLoading = true) }
            rmpRepository.getProfile().first().fold(
                onSuccess = { profile ->
                    _state.update { it.copy(profile = profile, profileLoading = false) }
                },
                onFailure = {
                    _state.update { it.copy(profileLoading = false) }
                }
            )
        }
    }

    fun showLearning() {
        _state.update { it.copy(showLearning = true, modulesLoading = true) }
        viewModelScope.launch {
            rmpRepository.getLearningModules().first().fold(
                onSuccess = { list ->
                    _state.update { it.copy(modules = list, modulesLoading = false) }
                },
                onFailure = {
                    _state.update { it.copy(modulesLoading = false) }
                }
            )
        }
    }

    fun hideLearning() {
        _state.update { it.copy(showLearning = false) }
    }

    fun showGuidance(emergencyId: String) {
        viewModelScope.launch {
            rmpRepository.getGuidance(emergencyId).first().fold(
                onSuccess = { steps ->
                    _state.update { it.copy(guidanceSteps = steps, showGuidance = true) }
                },
                onFailure = { }
            )
        }
    }

    fun hideGuidance() {
        _state.update { it.copy(showGuidance = false, guidanceSteps = null) }
    }
}
