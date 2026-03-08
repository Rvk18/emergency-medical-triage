package com.medtriage.app.ui.hospitals

import android.Manifest
import android.content.pm.PackageManager
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.platform.LocalContext
import androidx.core.content.ContextCompat
import androidx.hilt.navigation.compose.hiltViewModel

@Composable
fun HospitalsFlowScreen(
    selectedLangCode: String = "en",
    viewModel: HospitalsViewModel = hiltViewModel()
) {
    val state by viewModel.state.collectAsState()
    val context = LocalContext.current
    val hasLocationPermission = ContextCompat.checkSelfPermission(
        context,
        Manifest.permission.ACCESS_FINE_LOCATION
    ) == PackageManager.PERMISSION_GRANTED
    val locationPermissionLauncher = rememberLauncherForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { granted ->
        if (granted) {
            viewModel.refreshCurrentLocation { viewModel.loadMatches() }
        } else {
            viewModel.loadMatches()
        }
    }
    LaunchedEffect(Unit) {
        if (!hasLocationPermission) {
            viewModel.loadMatches()
            locationPermissionLauncher.launch(Manifest.permission.ACCESS_FINE_LOCATION)
        } else {
            viewModel.refreshCurrentLocation { viewModel.loadMatches() }
        }
    }

    when {
        state.showHandoff -> HandoffReportScreen(onDone = viewModel::handoffDone)
        state.selectedHospital != null -> NavigationScreen(
            hospital = state.selectedHospital!!,
            steps = state.routeSteps,
            routeResult = state.routeResult,
            startLocationLabel = if (state.currentLocation != null) "Current location" else "Default location (enable location for your position)",
            onGenerateHandoff = viewModel::showHandoffReport,
            onChangeHospital = viewModel::changeHospital
        )
        else -> HospitalMatchScreen(
            matches = state.matches,
            loading = state.loading,
            error = state.error,
            onNavigateToHospital = viewModel::selectHospital
        )
    }
}
