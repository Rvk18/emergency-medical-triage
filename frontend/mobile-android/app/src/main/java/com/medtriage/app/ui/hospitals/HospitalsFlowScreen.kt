package com.medtriage.app.ui.hospitals

import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.hilt.navigation.compose.hiltViewModel

@Composable
fun HospitalsFlowScreen(
    selectedLangCode: String = "en",
    viewModel: HospitalsViewModel = hiltViewModel()
) {
    val state by viewModel.state.collectAsState()

    when {
        state.showHandoff -> HandoffReportScreen(onDone = viewModel::handoffDone)
        state.selectedHospital != null -> NavigationScreen(
            hospital = state.selectedHospital!!,
            steps = state.routeSteps,
            routeResult = state.routeResult,
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
