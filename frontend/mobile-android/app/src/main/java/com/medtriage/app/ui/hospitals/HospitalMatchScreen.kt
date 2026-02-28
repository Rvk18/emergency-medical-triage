package com.medtriage.app.ui.hospitals

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.medtriage.app.data.hospitals.HospitalMatch
import com.medtriage.app.ui.theme.Spacing

@Composable
fun HospitalMatchScreen(
    matches: List<HospitalMatch>,
    loading: Boolean,
    error: String?,
    onNavigateToHospital: (HospitalMatch) -> Unit
) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(Spacing.space16)
            .verticalScroll(rememberScrollState())
    ) {
        Text("Top 3 hospital matches", style = MaterialTheme.typography.titleLarge)
        Spacer(Modifier.height(Spacing.space16))
        if (loading) Text("Loading…")
        error?.let { Text(it, color = MaterialTheme.colorScheme.error) }
        matches.forEach { hospital ->
            HospitalCard(
                hospital = hospital,
                onNavigate = { onNavigateToHospital(hospital) }
            )
            Spacer(Modifier.height(Spacing.space12))
        }
    }
}

@Composable
private fun HospitalCard(
    hospital: HospitalMatch,
    onNavigate: () -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(modifier = Modifier.padding(Spacing.space16)) {
            Text(hospital.name, style = MaterialTheme.typography.titleMedium)
            Text("${hospital.distanceKm} km • ETA ${hospital.etaMinutes} min", style = MaterialTheme.typography.bodyMedium)
            Text("Beds: ${hospital.bedsAvailable}/${hospital.bedsTotal}", style = MaterialTheme.typography.bodySmall)
            Text("Specialist on-call: ${if (hospital.specialistOnCall) "Yes" else "No"}", style = MaterialTheme.typography.bodySmall)
            Text("Match score: ${hospital.matchScorePercent}%", style = MaterialTheme.typography.labelLarge)
            Spacer(Modifier.height(Spacing.space8))
            androidx.compose.material3.Button(onClick = onNavigate, modifier = Modifier.fillMaxWidth()) {
                Text("Navigate")
            }
        }
    }
}
