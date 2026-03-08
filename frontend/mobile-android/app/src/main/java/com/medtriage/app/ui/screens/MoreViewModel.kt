package com.medtriage.app.ui.screens

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.medtriage.app.data.health.HealthRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

data class MoreUiState(
    val healthCheckLoading: Boolean = false,
    val healthCheckMessage: String? = null,
    val healthCheckSuccess: Boolean? = null
)

@HiltViewModel
class MoreViewModel @Inject constructor(
    private val healthRepository: HealthRepository
) : ViewModel() {

    private val _state = MutableStateFlow(MoreUiState())
    val state: StateFlow<MoreUiState> = _state.asStateFlow()

    fun checkApiStatus() {
        viewModelScope.launch {
            _state.value = _state.value.copy(healthCheckLoading = true, healthCheckMessage = null)
            healthRepository.checkHealth()
                .fold(
                    onSuccess = { resp ->
                        _state.value = _state.value.copy(
                            healthCheckLoading = false,
                            healthCheckMessage = "API OK: ${resp.status ?: "ok"}",
                            healthCheckSuccess = true
                        )
                    },
                    onFailure = { e ->
                        _state.value = _state.value.copy(
                            healthCheckLoading = false,
                            healthCheckMessage = "API error: ${e.message}",
                            healthCheckSuccess = false
                        )
                    }
                )
        }
    }

    fun clearHealthCheckMessage() {
        _state.value = _state.value.copy(healthCheckMessage = null, healthCheckSuccess = null)
    }
}
