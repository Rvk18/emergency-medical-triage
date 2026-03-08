package com.medtriage.app.ui.components

import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Cloud
import androidx.compose.material.icons.filled.CloudDone
import androidx.compose.material.icons.filled.CloudOff
import androidx.compose.material.icons.filled.Sync
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.medtriage.app.ui.theme.Spacing
import com.medtriage.app.ui.theme.SuccessColor
import com.medtriage.app.ui.theme.WarningColor

enum class SyncStatus {
    Synced,
    Pending,
    Syncing,
    Failed
}

@Composable
fun SyncStatusIndicator(
    status: SyncStatus,
    modifier: Modifier = Modifier,
    lastSyncTime: String? = null
) {
    val (icon, label, tint) = when (status) {
        SyncStatus.Synced -> Triple(Icons.Default.CloudDone, "Synced", SuccessColor)
        SyncStatus.Pending -> Triple(Icons.Default.Cloud, "Pending", WarningColor)
        SyncStatus.Syncing -> Triple(Icons.Default.Sync, "Syncing…", MaterialTheme.colorScheme.primary)
        SyncStatus.Failed -> Triple(Icons.Default.CloudOff, "Failed", MaterialTheme.colorScheme.error)
    }
    Row(
        modifier = modifier.padding(horizontal = Spacing.space8),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Icon(
            imageVector = icon,
            contentDescription = label,
            modifier = Modifier.size(18.dp),
            tint = tint
        )
        Text(
            text = lastSyncTime?.let { "$label • $it" } ?: label,
            style = MaterialTheme.typography.labelSmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
    }
}
