package com.medtriage.app.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.unit.dp
import com.medtriage.app.ui.theme.SeverityCritical
import com.medtriage.app.ui.theme.SeverityLow
import com.medtriage.app.ui.theme.Spacing
import com.medtriage.app.ui.theme.WarningColor

@Composable
fun ConfidenceBar(
    confidencePercent: Int,
    modifier: Modifier = Modifier
) {
    val progress = (confidencePercent / 100f).coerceIn(0f, 1f)
    val segmentColor = when {
        progress >= 0.85f -> SeverityLow
        progress >= 0.70f -> WarningColor
        else -> SeverityCritical
    }
    Row(
        modifier = modifier.fillMaxWidth(),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Box(
            modifier = Modifier
                .weight(1f)
                .height(8.dp)
                .clip(RoundedCornerShape(4.dp))
                .background(MaterialTheme.colorScheme.surfaceVariant)
        ) {
            if (progress > 0f) {
                Box(
                    modifier = Modifier
                        .fillMaxHeight()
                        .fillMaxWidth(progress)
                        .clip(RoundedCornerShape(4.dp))
                        .background(segmentColor)
                )
            }
        }
        Box(modifier = Modifier.width(Spacing.space12))
        Text(
            text = "$confidencePercent%",
            style = MaterialTheme.typography.labelLarge,
            color = MaterialTheme.colorScheme.onSurface
        )
    }
}
