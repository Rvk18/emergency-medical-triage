package com.medtriage.app.ui.screens

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Fingerprint
import androidx.compose.material3.Button
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import com.medtriage.app.ui.theme.Spacing

@Composable
fun LoginScreen(
    onLoginSuccess: () -> Unit,
    onLogin: (emailOrPhone: String, password: String, onResult: (Result<Unit>) -> Unit) -> Unit
) {
    var emailOrPhone by rememberSaveable { mutableStateOf("") }
    var password by rememberSaveable { mutableStateOf("") }
    var error by rememberSaveable { mutableStateOf<String?>(null) }
    var isLoading by rememberSaveable { mutableStateOf(false) }

    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(Spacing.space24),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(
            text = "MedTriage AI",
            style = MaterialTheme.typography.headlineMedium,
            modifier = Modifier.padding(bottom = Spacing.space32)
        )
        OutlinedTextField(
            value = emailOrPhone,
            onValueChange = { emailOrPhone = it; error = null },
            label = { Text("Email or phone") },
            singleLine = true,
            modifier = Modifier.fillMaxWidth(),
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Email)
        )
        Spacer(modifier = Modifier.height(Spacing.space16))
        OutlinedTextField(
            value = password,
            onValueChange = { password = it; error = null },
            label = { Text("Password") },
            singleLine = true,
            visualTransformation = PasswordVisualTransformation(),
            modifier = Modifier.fillMaxWidth(),
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password)
        )
        Spacer(modifier = Modifier.height(Spacing.space8))
        IconButton(onClick = { /* Biometric placeholder */ }) {
            Icon(Icons.Default.Fingerprint, contentDescription = "Sign in with biometrics")
        }
        Text(
            text = "Biometric sign-in (placeholder)",
            style = MaterialTheme.typography.bodySmall
        )
        Spacer(modifier = Modifier.height(Spacing.space24))
        error?.let { Text(it, color = MaterialTheme.colorScheme.error) }
        Spacer(modifier = Modifier.height(Spacing.space8))
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
            enabled = !isLoading
        ) {
            Text(if (isLoading) "Signing in…" else "Sign in")
        }
    }
}
