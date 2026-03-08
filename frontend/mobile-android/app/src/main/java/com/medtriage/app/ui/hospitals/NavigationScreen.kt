package com.medtriage.app.ui.hospitals

import android.content.Intent
import android.net.Uri
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.style.TextAlign
import com.medtriage.app.data.hospitals.HospitalMatch
import com.medtriage.app.data.hospitals.RouteResult
import com.medtriage.app.data.hospitals.RouteStep
import com.medtriage.app.ui.theme.Spacing
import java.net.URLEncoder

@Composable
fun NavigationScreen(
    hospital: HospitalMatch,
    steps: List<RouteStep>,
    routeResult: RouteResult? = null,
    startLocationLabel: String? = null,
    onGenerateHandoff: () -> Unit,
    onChangeHospital: () -> Unit
) {
    val context = LocalContext.current
    var showMapsDialog by remember { mutableStateOf(false) }

    val mapsUrl: String = remember(routeResult, hospital) {
        when {
            hospital.lat != null && hospital.lon != null ->
                "https://www.google.com/maps/dir/?api=1&destination=${hospital.lat},${hospital.lon}&travelmode=driving"
            !routeResult?.directionsUrl.isNullOrBlank() -> routeResult!!.directionsUrl!!
            else ->
                "https://www.google.com/maps/search/?api=1&query=${URLEncoder.encode(hospital.name, "UTF-8")}"
        }
    }

    if (showMapsDialog) {
        AlertDialog(
            onDismissRequest = { showMapsDialog = false },
            title = { Text("Open in Google Maps", textAlign = TextAlign.Center) },
            text = { Text("Navigate to ${hospital.name} using your maps app?") },
            confirmButton = {
                Button(
                    onClick = {
                        showMapsDialog = false
                        val intent = Intent(Intent.ACTION_VIEW, Uri.parse(mapsUrl))
                        context.startActivity(Intent.createChooser(intent, "Open with"))
                    }
                ) {
                    Text("Open")
                }
            },
            dismissButton = {
                TextButton(onClick = { showMapsDialog = false }) {
                    Text("Cancel")
                }
            }
        )
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(Spacing.space16)
    ) {
        Text("Navigation to ${hospital.name}", style = MaterialTheme.typography.titleLarge)
        startLocationLabel?.let { label ->
            Text("From: $label", style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
        }
        val etaMin = routeResult?.durationMinutes ?: hospital.etaMinutes
        Text("ETA: $etaMin min", style = MaterialTheme.typography.bodyLarge)
        routeResult?.let { r ->
            Text("${r.distanceKm} km", style = MaterialTheme.typography.bodyMedium)
        }
        Spacer(Modifier.height(Spacing.space16))
        Button(
            onClick = { showMapsDialog = true },
            modifier = Modifier.fillMaxWidth()
        ) {
            Text("Open in Google Maps")
        }
        Spacer(Modifier.height(Spacing.space8))
        Text("Turn-by-turn:", style = MaterialTheme.typography.labelLarge)
        Column(modifier = Modifier.verticalScroll(rememberScrollState())) {
            steps.forEachIndexed { i, step ->
                Text("${i + 1}. ${step.instruction}", style = MaterialTheme.typography.bodyMedium)
            }
        }
        Spacer(Modifier.height(Spacing.space24))
        Button(onClick = onChangeHospital, modifier = Modifier.fillMaxWidth()) { Text("Change hospital") }
        Spacer(Modifier.height(Spacing.space8))
        Button(onClick = onGenerateHandoff, modifier = Modifier.fillMaxWidth()) { Text("Generate Handoff Report") }
    }
}
