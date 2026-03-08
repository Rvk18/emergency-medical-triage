package com.medtriage.app.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import com.medtriage.app.data.triage.SeverityLevel
import com.medtriage.app.ui.theme.SeverityCritical
import com.medtriage.app.ui.theme.SeverityCriticalSurface
import com.medtriage.app.ui.theme.SeverityHigh
import com.medtriage.app.ui.theme.SeverityHighSurface
import com.medtriage.app.ui.theme.SeverityLow
import com.medtriage.app.ui.theme.SeverityLowSurface
import com.medtriage.app.ui.theme.SeverityMedium
import com.medtriage.app.ui.theme.SeverityMediumSurface
import com.medtriage.app.ui.theme.Spacing

@Composable
fun SeverityChip(
    severity: SeverityLevel,
    modifier: Modifier = Modifier,
    selectedLangCode: String = "en",
    label: String = com.medtriage.app.ui.utils.Translator.t(severity.name.lowercase().replaceFirstChar { it.uppercase() }, selectedLangCode)
) {
    val (surface, onSurface) = when (severity) {
        SeverityLevel.CRITICAL -> SeverityCriticalSurface to SeverityCritical
        SeverityLevel.HIGH -> SeverityHighSurface to SeverityHigh
        SeverityLevel.MEDIUM -> SeverityMediumSurface to SeverityMedium
        SeverityLevel.LOW -> SeverityLowSurface to SeverityLow
    }
    Box(
        modifier = modifier
            .background(surface, MaterialTheme.shapes.small)
            .padding(horizontal = Spacing.space12, vertical = Spacing.space8)
    ) {
        Text(
            text = label,
            style = MaterialTheme.typography.labelLarge,
            color = onSurface
        )
    }
}
