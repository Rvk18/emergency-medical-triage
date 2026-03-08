package com.medtriage.app.ui.hospitals

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
import com.medtriage.app.data.hospitals.HospitalMatch
import com.medtriage.app.ui.components.EmptyState
import com.medtriage.app.ui.components.SectionCard
import com.medtriage.app.ui.components.SkeletonCard
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
            .padding(Spacing.screenHorizontal)
            .verticalScroll(rememberScrollState())
    ) {
        Text("Top 3 hospital matches", style = MaterialTheme.typography.headlineSmall, color = MaterialTheme.colorScheme.onSurface)
        Text("Choose a hospital to navigate", style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant, modifier = Modifier.padding(top = Spacing.space4))
        Spacer(Modifier.height(Spacing.sectionGap))
        error?.let { Text(it, color = MaterialTheme.colorScheme.error, style = MaterialTheme.typography.bodySmall) }
        when {
            loading -> {
                repeat(3) {
                    SkeletonCard(modifier = Modifier.padding(bottom = Spacing.space16))
                }
            }
            matches.isEmpty() -> {
                EmptyState(
                    title = "No matches",
                    description = "No hospitals matched the criteria. Adjust filters or try again later."
                )
            }
            else -> {
                matches.forEach { hospital ->
                    HospitalCard(hospital = hospital, onNavigate = { onNavigateToHospital(hospital) })
                    Spacer(Modifier.height(Spacing.space16))
                }
            }
        }
        Spacer(Modifier.height(Spacing.space40))
    }
}

@Composable
private fun HospitalCard(
    hospital: HospitalMatch,
    onNavigate: () -> Unit
) {
    SectionCard(title = null) {
        Text(hospital.name, style = MaterialTheme.typography.titleMedium, color = MaterialTheme.colorScheme.primary)
        Spacer(Modifier.height(Spacing.space8))
        Text("${hospital.distanceKm} km • ETA ${hospital.etaMinutes} min", style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
        Text("Beds: ${hospital.bedsAvailable}/${hospital.bedsTotal}", style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
        Text("Specialist on-call: ${if (hospital.specialistOnCall) "Yes" else "No"}", style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
        Spacer(Modifier.height(Spacing.space12))
        Text("Match score: ${hospital.matchScorePercent}%", style = MaterialTheme.typography.labelLarge, color = MaterialTheme.colorScheme.primary)
        Spacer(Modifier.height(Spacing.space12))
        androidx.compose.material3.Button(onClick = onNavigate, modifier = Modifier.fillMaxWidth()) {
            Text("Navigate")
        }
    }
}
