package com.medtriage.app.ui.hospitals

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.medtriage.app.data.hospitals.HospitalMatch
import com.medtriage.app.data.hospitals.HospitalRepository
import com.medtriage.app.data.hospitals.RouteStep
import com.medtriage.app.data.location.LocationRepository
import com.medtriage.app.data.location.LocationResult
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
    val showHandoff: Boolean = false,
    /** Current GPS location; used as route origin and sent as patient_location to POST /hospitals. */
    val currentLocation: LocationResult? = null,
    val locationLoading: Boolean = false
)

@HiltViewModel
class HospitalsViewModel @Inject constructor(
    private val hospitalRepository: HospitalRepository,
    private val locationRepository: LocationRepository
) : ViewModel() {

    private val _state = MutableStateFlow(HospitalsUiState())
    val state: StateFlow<HospitalsUiState> = _state.asStateFlow()

    init {
        viewModelScope.launch {
            refreshCurrentLocation()
        }
    }

    /** Fetches current GPS location and stores it for route origin and POST /hospitals patient_location. */
    fun refreshCurrentLocation(onDone: (() -> Unit)? = null) {
        viewModelScope.launch {
            if (!locationRepository.hasLocationPermission()) {
                onDone?.invoke()
                return@launch
            }
            _state.update { it.copy(locationLoading = true) }
            val loc = locationRepository.getLastKnownLocation()
                ?: locationRepository.getCurrentLocation().getOrNull()
            _state.update {
                it.copy(currentLocation = loc, locationLoading = false)
            }
            onDone?.invoke()
        }
    }

    /** Current device location from state or last known; null if never fetched. */
    private fun getDeviceLocation(): Pair<Double, Double>? =
        _state.value.currentLocation?.toPair() ?: locationRepository.getLastKnownLocation()?.toPair()

    /**
     * Load hospital matches. Sends current location as patient_location_lat/lon when available
     * (backend returns distance_km, duration_minutes, directions_url per hospital).
     */
    fun loadMatches() {
        viewModelScope.launch {
            _state.update { it.copy(loading = true, error = null) }
            val loc = _state.value.currentLocation ?: locationRepository.getLastKnownLocation()
            val lat = loc?.latitude
            val lon = loc?.longitude
            hospitalRepository.getMatches(patientLocationLat = lat, patientLocationLon = lon).first().fold(
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

    /** Origin for POST /route: current GPS when available, else default (per backend openapi origin + destination). */
    private fun routeOriginLatLon(): Pair<Double, Double> =
        getDeviceLocation() ?: (defaultOriginLat to defaultOriginLon)

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
                var (originLat, originLon) = routeOriginLatLon()
                if (_state.value.currentLocation == null && locationRepository.hasLocationPermission()) {
                    _state.update { it.copy(locationLoading = true) }
                    val loc = locationRepository.getLastKnownLocation()
                        ?: locationRepository.getCurrentLocation().getOrNull()
                    if (loc != null) {
                        _state.update {
                            it.copy(currentLocation = loc, locationLoading = false)
                        }
                        originLat = loc.latitude
                        originLon = loc.longitude
                    } else {
                        _state.update { it.copy(locationLoading = false) }
                    }
                }
                hospitalRepository.getRoute(
                    originLat,
                    originLon,
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
