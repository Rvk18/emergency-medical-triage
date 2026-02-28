package com.medtriage.app.ui.screens

import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import com.medtriage.app.ui.theme.Spacing

@Composable
fun DashboardPlaceholderScreen() {
    Box(
        modifier = Modifier
            .fillMaxSize()
            .padding(Spacing.space16),
        contentAlignment = Alignment.Center
    ) {
        Text("Dashboard — RMP profile and stats (Phase 5)")
    }
}
