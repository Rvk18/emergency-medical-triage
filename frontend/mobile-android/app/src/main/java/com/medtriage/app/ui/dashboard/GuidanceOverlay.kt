package com.medtriage.app.ui.dashboard

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import com.medtriage.app.data.rmp.GuidanceStep
import com.medtriage.app.ui.theme.Spacing

@Composable
fun GuidanceOverlay(
    steps: List<GuidanceStep>,
    onDismiss: () -> Unit
) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(Spacing.space16)
            .verticalScroll(rememberScrollState())
    ) {
        Text("Procedural guidance", style = MaterialTheme.typography.titleLarge)
        Spacer(Modifier.height(Spacing.space16))
        steps.forEach { step ->
            Text("${step.number}. ${step.title}", style = MaterialTheme.typography.titleMedium)
            Text(step.description, style = MaterialTheme.typography.bodyMedium)
            Spacer(Modifier.height(Spacing.space8))
        }
        Spacer(Modifier.height(Spacing.space16))
        androidx.compose.material3.Button(onClick = onDismiss, modifier = Modifier.fillMaxWidth()) {
            Text("Dismiss")
        }
    }
}
