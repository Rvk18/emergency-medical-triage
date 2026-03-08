package com.medtriage.app.ui.hospitals

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.medtriage.app.data.hospitals.HospitalMatch
import com.medtriage.app.data.hospitals.HospitalRepository
import com.medtriage.app.data.hospitals.RouteStep
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject

data class HospitalsUiState(
    val matches: List<HospitalMatch> = emptyList(),
    val loading: Boolean = true,
    val error: String? = null,
    val selectedHospital: HospitalMatch? = null,
    val routeSteps: List<RouteStep> = emptyList(),
    val routeResult: com.medtriage.app.data.hospitals.RouteResult? = null,
    val showHandoff: Boolean = false
)

@HiltViewModel
class HospitalsViewModel @Inject constructor(
    private val hospitalRepository: HospitalRepository
) : ViewModel() {

    private val _state = MutableStateFlow(HospitalsUiState())
    val state: StateFlow<HospitalsUiState> = _state.asStateFlow()

    init {
        loadMatches()
    }

    fun loadMatches() {
        viewModelScope.launch {
            _state.update { it.copy(loading = true, error = null) }
            hospitalRepository.getMatches().first().fold(
                onSuccess = { list ->
                    _state.update { it.copy(matches = list, loading = false) }
                },
                onFailure = { e ->
                    _state.update { it.copy(loading = false, error = e.message) }
                }
            )
        }
    }

    /** Default origin for route (e.g. Bangalore) when device location not available. */
    private val defaultOriginLat = 12.9716
    private val defaultOriginLon = 77.5946

    fun selectHospital(hospital: HospitalMatch) {
        viewModelScope.launch {
            _state.update {
                it.copy(
                    selectedHospital = hospital,
                    routeSteps = emptyList(),
                    routeResult = null
                )
            }
            if (hospital.lat != null && hospital.lon != null) {
                hospitalRepository.getRoute(
                    defaultOriginLat,
                    defaultOriginLon,
                    hospital.lat,
                    hospital.lon
                ).fold(
                    onSuccess = { routeResult ->
                        _state.update { it.copy(routeResult = routeResult) }
                    },
                    onFailure = { }
                )
            }
            hospitalRepository.getRouteSteps(hospital.id).first().fold(
                onSuccess = { steps ->
                    _state.update { it.copy(routeSteps = steps) }
                },
                onFailure = { }
            )
        }
    }

    fun changeHospital() {
        _state.update { it.copy(selectedHospital = null, routeSteps = emptyList(), routeResult = null) }
    }

    fun showHandoffReport() {
        _state.update { it.copy(showHandoff = true) }
    }

    fun handoffDone() {
        _state.update { it.copy(showHandoff = false, selectedHospital = null, routeSteps = emptyList(), routeResult = null) }
    }
}
