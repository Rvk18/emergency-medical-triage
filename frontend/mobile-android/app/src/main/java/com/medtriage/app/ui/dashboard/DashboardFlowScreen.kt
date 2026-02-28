package com.medtriage.app.ui.dashboard

import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.ModalBottomSheet
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.hilt.navigation.compose.hiltViewModel

@Composable
fun DashboardFlowScreen(
    viewModel: DashboardViewModel = hiltViewModel(),
    onNavigateToTriage: () -> Unit,
    onNavigateToHospitals: () -> Unit
) {
    val state by viewModel.state.collectAsState()

    Box(Modifier.fillMaxSize()) {
        when {
            state.showLearning -> LearningScreen(
                modules = state.modules,
                loading = state.modulesLoading,
                onBack = { viewModel.hideLearning() }
            )
            else -> RmpDashboardScreen(
                profile = state.profile,
                loading = state.profileLoading,
                onStartTriage = onNavigateToTriage,
                onShowLearning = { viewModel.showLearning() }
            )
        }
    }

    if (state.showGuidance && state.guidanceSteps != null) {
        ModalBottomSheet(
            onDismissRequest = { viewModel.hideGuidance() }
        ) {
            GuidanceOverlay(
                steps = state.guidanceSteps!!,
                onDismiss = { viewModel.hideGuidance() }
            )
        }
    }
}
