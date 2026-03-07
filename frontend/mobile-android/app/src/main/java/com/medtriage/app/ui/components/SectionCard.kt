package com.medtriage.app.ui.components

import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ColumnScope
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.medtriage.app.ui.theme.SeverityCritical
import com.medtriage.app.ui.theme.SeverityCriticalSurface
import com.medtriage.app.ui.theme.Spacing
import com.medtriage.app.ui.theme.WarningColor
import com.medtriage.app.ui.theme.WarningSurface

enum class SectionCardVariant {
    Default,
    Info,
    Warning,
    Critical
}

@Composable
fun SectionCard(
    modifier: Modifier = Modifier,
    title: String? = null,
    variant: SectionCardVariant = SectionCardVariant.Default,
    content: @Composable ColumnScope.() -> Unit
) {
    val (containerColor, borderColor) = when (variant) {
        SectionCardVariant.Default -> MaterialTheme.colorScheme.surface to null
        SectionCardVariant.Info -> MaterialTheme.colorScheme.surface to MaterialTheme.colorScheme.primary
        SectionCardVariant.Warning -> WarningSurface to WarningColor
        SectionCardVariant.Critical -> SeverityCriticalSurface to SeverityCritical
    }
    Card(
        modifier = modifier
            .fillMaxWidth()
            .then(
                if (borderColor != null) Modifier.border(2.dp, borderColor, MaterialTheme.shapes.medium)
                else Modifier
            ),
        shape = MaterialTheme.shapes.medium,
        elevation = CardDefaults.cardElevation(defaultElevation = 1.dp),
        colors = CardDefaults.cardColors(containerColor = containerColor)
    ) {
        Column(modifier = Modifier.padding(Spacing.cardPadding)) {
            title?.let {
                Text(
                    text = it,
                    style = MaterialTheme.typography.titleSmall,
                    color = when (variant) {
                        SectionCardVariant.Warning -> WarningColor
                        SectionCardVariant.Critical -> SeverityCritical
                        else -> MaterialTheme.colorScheme.onSurfaceVariant
                    },
                    modifier = Modifier.padding(bottom = Spacing.space12)
                )
            }
            content()
        }
    }
}
