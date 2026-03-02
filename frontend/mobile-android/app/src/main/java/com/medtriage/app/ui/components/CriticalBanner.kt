package com.medtriage.app.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import com.medtriage.app.ui.theme.SeverityCritical
import com.medtriage.app.ui.theme.SeverityCriticalSurface
import com.medtriage.app.ui.theme.Spacing

/**
 * Persistent banner for Critical severity. No dismiss.
 * Shown below app bar when active case is Critical.
 */
@Composable
fun CriticalBanner(
    message: String = "CRITICAL — Immediate transport. Do not delay.",
    modifier: Modifier = Modifier
) {
    Box(
        modifier = modifier
            .fillMaxWidth()
            .background(SeverityCriticalSurface)
            .padding(horizontal = Spacing.screenHorizontal, vertical = Spacing.space12),
        contentAlignment = Alignment.CenterStart
    ) {
        Text(
            text = message,
            style = MaterialTheme.typography.labelLarge,
            color = SeverityCritical
        )
    }
}
