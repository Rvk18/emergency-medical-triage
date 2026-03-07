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
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.DarkMode
import androidx.compose.material.icons.filled.LightMode
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.FilterChip
import androidx.compose.material3.FilterChipDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.OutlinedTextFieldDefaults
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import com.medtriage.app.ui.theme.MedTriagePrimary
import com.medtriage.app.ui.theme.Spacing

/** Dark blue-grey background when in dark mode (login). */
private val LoginScreenBackgroundDark = Color(0xFF1E293B)
private val LoginCardBackgroundDark = Color(0xFF334155)

/** Language options matching web: label + code. */
private val LOGIN_LANGUAGES = listOf(
    "en" to "English",
    "hi" to "हिन्दी",
    "ta" to "தமிழ்",
    "te" to "తెలుగు",
    "kn" to "ಕನ್ನಡ",
    "ml" to "മലയാളം",
    "bn" to "বাংলা"
)

@Composable
fun LoginScreen(
    darkTheme: Boolean = false,
    onDarkThemeChange: (Boolean) -> Unit = {},
    onLoginSuccess: () -> Unit,
    onLogin: (emailOrPhone: String, password: String, onResult: (Result<Unit>) -> Unit) -> Unit,
    onBackToRoleSelection: () -> Unit = {},
    onLanguageSelected: (languageCode: String) -> Unit = {},
    onSettingsClick: () -> Unit = {}
) {
    var emailOrPhone by rememberSaveable { mutableStateOf("") }
    var password by rememberSaveable { mutableStateOf("") }
    var error by rememberSaveable { mutableStateOf<String?>(null) }
    var isLoading by rememberSaveable { mutableStateOf(false) }
    var selectedLangCode by rememberSaveable { mutableStateOf("en") }

    val screenBackground = if (darkTheme) LoginScreenBackgroundDark else MaterialTheme.colorScheme.background
    val cardBackground = if (darkTheme) LoginCardBackgroundDark else MaterialTheme.colorScheme.surface
    val onBackgroundColor = if (darkTheme) Color.White else MaterialTheme.colorScheme.onBackground
    val onSurfaceColor = if (darkTheme) Color.White else MaterialTheme.colorScheme.onSurface

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(screenBackground)
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .verticalScroll(rememberScrollState())
        ) {
            // Top bar: Back + title area + Settings
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 8.dp, vertical = 8.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                IconButton(onClick = onBackToRoleSelection) {
                    Icon(
                        Icons.AutoMirrored.Filled.ArrowBack,
                        contentDescription = "Back",
                        tint = onBackgroundColor
                    )
                }
                TextButton(onClick = onBackToRoleSelection) {
                    Text("Change role", color = onBackgroundColor.copy(alpha = 0.9f))
                }
                Spacer(modifier = Modifier.weight(1f))
                Text(
                    "MedTriage AI",
                    style = MaterialTheme.typography.titleMedium,
                    color = onBackgroundColor
                )
                Spacer(modifier = Modifier.weight(1f))
                IconButton(onClick = { onDarkThemeChange(!darkTheme) }) {
                    Icon(
                        if (darkTheme) Icons.Default.LightMode else Icons.Default.DarkMode,
                        contentDescription = if (darkTheme) "Switch to light theme" else "Switch to dark theme",
                        tint = onBackgroundColor
                    )
                }
                IconButton(onClick = onSettingsClick) {
                    Icon(Icons.Default.Settings, contentDescription = "Settings", tint = onBackgroundColor)
                }
            }

            Spacer(modifier = Modifier.height(24.dp))

            // Central card
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = Spacing.screenHorizontal),
                shape = MaterialTheme.shapes.large,
                elevation = CardDefaults.cardElevation(defaultElevation = 4.dp),
                colors = CardDefaults.cardColors(containerColor = cardBackground)
            ) {
                Column(modifier = Modifier.padding(Spacing.cardPadding)) {
                    Text(
                        text = "MedTriage AI",
                        style = MaterialTheme.typography.headlineMedium,
                        color = onSurfaceColor
                    )
                    Text(
                        text = "Emergency Medical Triage System",
                        style = MaterialTheme.typography.bodyMedium,
                        color = onSurfaceColor.copy(alpha = 0.8f),
                        modifier = Modifier.padding(top = 4.dp)
                    )
                    Spacer(modifier = Modifier.height(20.dp))

                    // Language / भाषा
                    Text(
                        text = "Language / भाषा",
                        style = MaterialTheme.typography.labelLarge,
                        color = onSurfaceColor.copy(alpha = 0.9f),
                        modifier = Modifier.padding(bottom = 8.dp)
                    )
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(8.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        LOGIN_LANGUAGES.take(5).forEach { (code, label) ->
                            FilterChip(
                                selected = selectedLangCode == code,
                                onClick = {
                                    selectedLangCode = code
                                    onLanguageSelected(code)
                                },
                                label = { Text(label, color = if (selectedLangCode == code) Color.White else onSurfaceColor.copy(alpha = 0.9f)) },
                                colors = FilterChipDefaults.filterChipColors(
                                    selectedContainerColor = MedTriagePrimary,
                                    selectedLabelColor = Color.White,
                                    containerColor = if (darkTheme) LoginCardBackgroundDark.copy(alpha = 0.8f) else MaterialTheme.colorScheme.surfaceVariant,
                                    labelColor = onSurfaceColor.copy(alpha = 0.9f)
                                )
                            )
                        }
                    }
                    Row(
                        modifier = Modifier.fillMaxWidth().padding(top = 8.dp),
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        LOGIN_LANGUAGES.drop(5).forEach { (code, label) ->
                            FilterChip(
                                selected = selectedLangCode == code,
                                onClick = {
                                    selectedLangCode = code
                                    onLanguageSelected(code)
                                },
                                label = { Text(label, color = if (selectedLangCode == code) Color.White else onSurfaceColor.copy(alpha = 0.9f)) },
                                colors = FilterChipDefaults.filterChipColors(
                                    selectedContainerColor = MedTriagePrimary,
                                    selectedLabelColor = Color.White,
                                    containerColor = if (darkTheme) LoginCardBackgroundDark.copy(alpha = 0.8f) else MaterialTheme.colorScheme.surfaceVariant,
                                    labelColor = onSurfaceColor.copy(alpha = 0.9f)
                                )
                            )
                        }
                    }
                    Spacer(modifier = Modifier.height(20.dp))

                    OutlinedTextField(
                        value = emailOrPhone,
                        onValueChange = { emailOrPhone = it; error = null },
                        label = { Text("Email or Phone", color = onSurfaceColor.copy(alpha = 0.8f)) },
                        singleLine = true,
                        modifier = Modifier.fillMaxWidth(),
                        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Email),
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedTextColor = onSurfaceColor,
                            unfocusedTextColor = onSurfaceColor,
                            cursorColor = MedTriagePrimary,
                            focusedBorderColor = MedTriagePrimary,
                            unfocusedBorderColor = onSurfaceColor.copy(alpha = 0.5f),
                            focusedLabelColor = onSurfaceColor.copy(alpha = 0.9f),
                            unfocusedLabelColor = onSurfaceColor.copy(alpha = 0.7f)
                        )
                    )
                    Spacer(modifier = Modifier.height(16.dp))
                    OutlinedTextField(
                        value = password,
                        onValueChange = { password = it; error = null },
                        label = { Text("Password", color = onSurfaceColor.copy(alpha = 0.8f)) },
                        singleLine = true,
                        visualTransformation = PasswordVisualTransformation(),
                        modifier = Modifier.fillMaxWidth(),
                        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password),
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedTextColor = onSurfaceColor,
                            unfocusedTextColor = onSurfaceColor,
                            cursorColor = MedTriagePrimary,
                            focusedBorderColor = MedTriagePrimary,
                            unfocusedBorderColor = onSurfaceColor.copy(alpha = 0.5f),
                            focusedLabelColor = onSurfaceColor.copy(alpha = 0.9f),
                            unfocusedLabelColor = onSurfaceColor.copy(alpha = 0.7f)
                        )
                    )
                    Spacer(modifier = Modifier.height(24.dp))

                    Button(
                        onClick = {
                            error = null
                            isLoading = true
                            onLogin(emailOrPhone, password) { result ->
                                isLoading = false
                                result.fold(
                                    onSuccess = { onLoginSuccess() },
                                    onFailure = { error = it.message ?: "Login failed" }
                                )
                            }
                        },
                        modifier = Modifier.fillMaxWidth(),
                        enabled = !isLoading,
                        colors = ButtonDefaults.buttonColors(containerColor = MedTriagePrimary)
                    ) {
                        Text(if (isLoading) "Signing in…" else "Sign In")
                    }
                }
            }

            error?.let {
                Spacer(modifier = Modifier.height(12.dp))
                Text(
                    it,
                    color = Color(0xFFF87171),
                    style = MaterialTheme.typography.bodySmall,
                    modifier = Modifier.padding(horizontal = Spacing.screenHorizontal)
                )
            }
            Spacer(modifier = Modifier.height(48.dp))
        }
    }
}
