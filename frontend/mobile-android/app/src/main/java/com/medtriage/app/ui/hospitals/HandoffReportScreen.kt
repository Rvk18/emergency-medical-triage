package com.medtriage.app.ui.hospitals

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import com.medtriage.app.ui.theme.Spacing

@Composable
fun HandoffReportScreen(
    onDone: () -> Unit
) {
    Column(modifier = Modifier.fillMaxWidth().padding(Spacing.space24)) {
        Text("Handoff report generated", style = MaterialTheme.typography.titleLarge)
        Spacer(Modifier.height(Spacing.space16))
        Text("The handoff report has been created and can be shared with the receiving hospital.", style = MaterialTheme.typography.bodyMedium)
        Spacer(Modifier.height(Spacing.space24))
        androidx.compose.material3.Button(onClick = onDone, modifier = Modifier.fillMaxWidth()) {
            Text("Done")
        }
    }
}
