package com.medtriage.app.ui.patient

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.LocationOn
import androidx.compose.material.icons.filled.Person
import androidx.compose.material.icons.filled.Phone
import androidx.compose.material.icons.filled.Warning
import androidx.compose.material3.IconButton
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import com.medtriage.app.ui.components.SectionCard
import com.medtriage.app.ui.theme.Spacing

@Composable
fun PatientEmergencyRequestScreen(
    onBack: () -> Unit,
    onSubmit: () -> Unit
) {
    var name by rememberSaveable { mutableStateOf("") }
    var age by rememberSaveable { mutableStateOf("") }
    var phone by rememberSaveable { mutableStateOf("") }
    var location by rememberSaveable { mutableStateOf("") }
    var emergency by rememberSaveable { mutableStateOf("") }
    val scrollState = rememberScrollState()

    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(Spacing.screenHorizontal)
            .verticalScroll(scrollState)
    ) {
        Spacer(modifier = Modifier.height(Spacing.space8))
        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = androidx.compose.ui.Alignment.CenterVertically
        ) {
            IconButton(onClick = onBack) {
                Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
            }
            Card(
                modifier = Modifier.padding(end = Spacing.space12),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.errorContainer),
                shape = MaterialTheme.shapes.medium
            ) {
                Icon(
                    Icons.Default.Warning,
                    contentDescription = null,
                    modifier = Modifier.padding(12.dp),
                    tint = MaterialTheme.colorScheme.error
                )
            }
            Column(modifier = Modifier.weight(1f)) {
                Text("Emergency Request", style = MaterialTheme.typography.headlineSmall, color = MaterialTheme.colorScheme.onSurface)
                Text("Request immediate medical assistance", style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
            }
        }
        Spacer(modifier = Modifier.height(Spacing.space24))

        SectionCard(
            title = "In case of life-threatening emergency",
            variant = com.medtriage.app.ui.components.SectionCardVariant.Critical,
            modifier = Modifier.padding(bottom = Spacing.space24)
        ) {
            Text(
                "Call 108 (ambulance) or go to the nearest hospital immediately.",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurface
            )
        }

        OutlinedTextField(
            value = name,
            onValueChange = { name = it },
            label = { Text("Full Name *") },
            leadingIcon = { Icon(Icons.Default.Person, contentDescription = null) },
            modifier = Modifier.fillMaxWidth(),
            singleLine = true
        )
        Spacer(modifier = Modifier.height(Spacing.space16))
        Row(modifier = Modifier.fillMaxWidth()) {
            OutlinedTextField(
                value = age,
                onValueChange = { age = it },
                label = { Text("Age *") },
                modifier = Modifier.weight(1f),
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                singleLine = true
            )
            Spacer(modifier = Modifier.padding(horizontal = Spacing.space12))
            OutlinedTextField(
                value = phone,
                onValueChange = { phone = it },
                label = { Text("Phone *") },
                leadingIcon = { Icon(Icons.Default.Phone, contentDescription = null) },
                modifier = Modifier.weight(1f),
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Phone),
                singleLine = true
            )
        }
        Spacer(modifier = Modifier.height(Spacing.space16))
        OutlinedTextField(
            value = location,
            onValueChange = { location = it },
            label = { Text("Current Location *") },
            leadingIcon = { Icon(Icons.Default.LocationOn, contentDescription = null) },
            placeholder = { Text("Auto-detected via GPS") },
            modifier = Modifier.fillMaxWidth(),
            singleLine = true
        )
        Spacer(modifier = Modifier.height(Spacing.space16))
        OutlinedTextField(
            value = emergency,
            onValueChange = { emergency = it },
            label = { Text("Describe the Emergency *") },
            placeholder = { Text("Describe your symptoms or emergency situation...") },
            modifier = Modifier.fillMaxWidth(),
            minLines = 4,
            maxLines = 6
        )
        Spacer(modifier = Modifier.height(Spacing.space16))
        SectionCard(variant = com.medtriage.app.ui.components.SectionCardVariant.Info, modifier = Modifier.padding(bottom = Spacing.space16)) {
            Text(
                "A healthcare worker will review your request and contact you shortly. Please keep your phone accessible.",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurface
            )
        }
        Button(
            onClick = onSubmit,
            modifier = Modifier.fillMaxWidth(),
            colors = androidx.compose.material3.ButtonDefaults.buttonColors(containerColor = MaterialTheme.colorScheme.error)
        ) {
            Icon(Icons.Default.Warning, contentDescription = null, modifier = Modifier.padding(end = Spacing.space8))
            Text("Submit Emergency Request")
        }
        Spacer(modifier = Modifier.height(Spacing.space32))
    }
}
