package com.medtriage.app.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.DarkMode
import androidx.compose.material.icons.filled.LightMode
import androidx.compose.material.icons.filled.MedicalServices
import androidx.compose.material.icons.filled.Person
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedCard
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.medtriage.app.ui.utils.Translator
import com.medtriage.app.ui.theme.Spacing

@Composable
fun RoleSelectorScreen(
    darkTheme: Boolean = false,
    selectedLangCode: String = "en",
    onDarkThemeChange: (Boolean) -> Unit = {},
    onLanguageSelected: (String) -> Unit = {},
    onSelectRole: (role: String) -> Unit
) {
    val screenBackground = MaterialTheme.colorScheme.background
    val onBackgroundColor = MaterialTheme.colorScheme.onBackground
    val onSurfaceColor = MaterialTheme.colorScheme.onSurface

    val LOGIN_LANGUAGES = listOf(
        "en" to "English",
        "hi" to "हिन्दी",
        "ta" to "தமிழ்",
        "te" to "తెలుగు",
        "kn" to "ಕನ್ನಡ",
        "ml" to "മലയാളം",
        "bn" to "বাংলা"
    )

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(screenBackground)
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .statusBarsPadding()
                .verticalScroll(rememberScrollState())
        ) {
            // Top bar: title + theme toggle
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 8.dp, vertical = 8.dp),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.End
            ) {
                Spacer(modifier = Modifier.weight(1f))
                Text(
                    text = "MedTriage AI",
                    style = MaterialTheme.typography.titleMedium,
                    color = onBackgroundColor
                )
                Spacer(modifier = Modifier.weight(1f))
                IconButton(
                    onClick = { onDarkThemeChange(!darkTheme) },
                    modifier = Modifier.padding(8.dp)
                ) {
                    Icon(
                        imageVector = if (darkTheme) Icons.Default.LightMode else Icons.Default.DarkMode,
                        contentDescription = if (darkTheme) Translator.t("Switch to light theme", selectedLangCode) else Translator.t("Switch to dark theme", selectedLangCode),
                        tint = MaterialTheme.colorScheme.primary,
                        modifier = Modifier.size(28.dp)
                    )
                }
            }

            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(Spacing.screenHorizontal),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Spacer(modifier = Modifier.height(Spacing.space24))
                Icon(
                    imageVector = Icons.Default.MedicalServices,
                    contentDescription = null,
                    modifier = Modifier.size(64.dp),
                    tint = MaterialTheme.colorScheme.primary
                )
                Spacer(modifier = Modifier.height(Spacing.space16))
                Text(
                    text = Translator.t("MedTriage AI", selectedLangCode),
                    style = MaterialTheme.typography.headlineMedium,
                    color = MaterialTheme.colorScheme.primary
                )
                Text(
                    text = Translator.t("Emergency Medical Triage", selectedLangCode),
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    modifier = Modifier.padding(top = Spacing.space8)
                )
                Spacer(modifier = Modifier.height(Spacing.sectionGap))

                Text(
                    text = Translator.t("Select Your Role", selectedLangCode),
                    style = MaterialTheme.typography.titleLarge,
                    color = MaterialTheme.colorScheme.onSurface,
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(bottom = Spacing.space24)
                )

                Column(verticalArrangement = Arrangement.spacedBy(Spacing.space16)) {
                    Card(
                        onClick = { onSelectRole("healthcare_worker") },
                        modifier = Modifier.fillMaxWidth(),
                        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.primary),
                        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
                    ) {
                        Row(
                            modifier = Modifier.padding(Spacing.cardPadding),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Icon(
                                imageVector = Icons.Default.MedicalServices,
                                contentDescription = null,
                                modifier = Modifier.size(48.dp),
                                tint = MaterialTheme.colorScheme.onPrimary
                            )
                            Spacer(modifier = Modifier.size(Spacing.space16))
                            Column(modifier = Modifier.weight(1f)) {
                                Text(
                                    text = Translator.t("Healthcare Worker", selectedLangCode),
                                    style = MaterialTheme.typography.titleMedium,
                                    color = MaterialTheme.colorScheme.onPrimary
                                )
                                Text(
                                    text = Translator.t("RMP, Nurse, or Medical Professional", selectedLangCode),
                                    style = MaterialTheme.typography.bodySmall,
                                    color = MaterialTheme.colorScheme.onPrimary.copy(alpha = 0.9f)
                                )
                            }
                        }
                    }

                    OutlinedCard(
                        onClick = { onSelectRole("patient") },
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Row(
                            modifier = Modifier.padding(Spacing.cardPadding),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Icon(
                                imageVector = Icons.Default.Person,
                                contentDescription = null,
                                modifier = Modifier.size(48.dp),
                                tint = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                            Spacer(modifier = Modifier.size(Spacing.space16))
                            Column(modifier = Modifier.weight(1f)) {
                                Text(
                                    text = Translator.t("Patient / User", selectedLangCode),
                                    style = MaterialTheme.typography.titleMedium,
                                    color = MaterialTheme.colorScheme.onSurface
                                )
                                Text(
                                    text = Translator.t("Request medical assistance", selectedLangCode),
                                    style = MaterialTheme.typography.bodySmall,
                                    color = MaterialTheme.colorScheme.onSurfaceVariant
                                )
                            }
                        }
                    }
                }

                Spacer(modifier = Modifier.height(Spacing.space24))
                
                // Language Selection Block
                Text(
                    text = Translator.t("Language / भाषा", selectedLangCode),
                    style = MaterialTheme.typography.labelLarge,
                    color = onSurfaceColor.copy(alpha = 0.9f),
                    modifier = Modifier.padding(bottom = 8.dp)
                )
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    LOGIN_LANGUAGES.take(4).forEach { (code, label) ->
                        androidx.compose.material3.FilterChip(
                            selected = selectedLangCode == code,
                            onClick = { onLanguageSelected(code) },
                            label = { Text(label, color = if (selectedLangCode == code) androidx.compose.ui.graphics.Color.White else onSurfaceColor.copy(alpha = 0.9f)) },
                            colors = androidx.compose.material3.FilterChipDefaults.filterChipColors(
                                selectedContainerColor = MaterialTheme.colorScheme.primary,
                                selectedLabelColor = androidx.compose.ui.graphics.Color.White,
                                containerColor = if (darkTheme) MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.8f) else MaterialTheme.colorScheme.surfaceVariant,
                            )
                        )
                    }
                }
                Row(
                    modifier = Modifier.fillMaxWidth().padding(top = 8.dp),
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    LOGIN_LANGUAGES.drop(4).forEach { (code, label) ->
                        androidx.compose.material3.FilterChip(
                            selected = selectedLangCode == code,
                            onClick = { onLanguageSelected(code) },
                            label = { Text(label, color = if (selectedLangCode == code) androidx.compose.ui.graphics.Color.White else onSurfaceColor.copy(alpha = 0.9f)) },
                            colors = androidx.compose.material3.FilterChipDefaults.filterChipColors(
                                selectedContainerColor = MaterialTheme.colorScheme.primary,
                                selectedLabelColor = androidx.compose.ui.graphics.Color.White,
                                containerColor = if (darkTheme) MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.8f) else MaterialTheme.colorScheme.surfaceVariant,
                            )
                        )
                    }
                }
                Spacer(modifier = Modifier.height(Spacing.space24))

                Text(
                    text = Translator.t("Your selection will determine your access level", selectedLangCode),
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                Spacer(modifier = Modifier.height(Spacing.space48))
            }
        }
    }
}
