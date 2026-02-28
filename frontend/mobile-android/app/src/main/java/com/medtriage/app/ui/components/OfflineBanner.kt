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
import androidx.compose.ui.unit.dp
import com.medtriage.app.ui.theme.OfflineBannerBackground
import com.medtriage.app.ui.theme.OfflineBannerText
import com.medtriage.app.ui.theme.Spacing

@Composable
fun OfflineBanner(
    visible: Boolean,
    lastSyncTime: String?,
    modifier: Modifier = Modifier
) {
    if (!visible) return
    Box(
        modifier = modifier
            .fillMaxWidth()
            .background(OfflineBannerBackground)
            .padding(horizontal = Spacing.space16, vertical = Spacing.space8),
        contentAlignment = Alignment.Center
    ) {
        Text(
            text = "OFFLINE MODE — LIMITED FUNCTIONALITY" + (lastSyncTime?.let { " • Last sync: $it" } ?: ""),
            color = OfflineBannerText,
            style = MaterialTheme.typography.labelLarge
        )
    }
}
