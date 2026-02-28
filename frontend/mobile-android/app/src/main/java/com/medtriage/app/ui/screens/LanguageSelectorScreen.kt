package com.medtriage.app.ui.screens

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.FilterChip
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.medtriage.app.ui.theme.Spacing

val SUPPORTED_LANGUAGES = listOf(
    "hi" to "Hindi",
    "en" to "English",
    "ta" to "Tamil",
    "te" to "Telugu",
    "bn" to "Bengali",
    "mr" to "Marathi",
    "gu" to "Gujarati"
)

@Composable
fun LanguageSelectorScreen(
    onLanguageSelected: (languageCode: String) -> Unit
) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(Spacing.space24)
            .verticalScroll(rememberScrollState())
    ) {
        Text(
            text = "Select language",
            style = MaterialTheme.typography.headlineMedium,
            modifier = Modifier.padding(bottom = Spacing.space24)
        )
        Column(
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            SUPPORTED_LANGUAGES.forEach { (code, name) ->
                FilterChip(
                    selected = false,
                    onClick = { onLanguageSelected(code) },
                    label = { Text(name) },
                    modifier = Modifier.fillMaxWidth()
                )
            }
        }
    }
}
