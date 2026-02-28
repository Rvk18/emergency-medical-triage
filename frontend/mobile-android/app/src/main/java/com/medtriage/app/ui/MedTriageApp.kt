package com.medtriage.app.ui

import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.hilt.navigation.compose.hiltViewModel
import com.medtriage.app.ui.auth.AuthViewModel
import com.medtriage.app.ui.screens.LanguageSelectorScreen
import com.medtriage.app.ui.screens.LoginScreen
import com.medtriage.app.ui.shell.AppShell

@Composable
fun MedTriageApp(
    authViewModel: AuthViewModel = hiltViewModel()
) {
    val authState by authViewModel.authState.collectAsState()

    when {
        authState.isLoading -> {
            Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                CircularProgressIndicator()
            }
        }
        !authState.isLoggedIn -> {
            LoginScreen(
                onLoginSuccess = { },
                onLogin = { email, password, onResult ->
                    authViewModel.login(email, password, onResult)
                }
            )
        }
        !authState.hasLanguageSelected -> {
            LanguageSelectorScreen(
                onLanguageSelected = { code ->
                    authViewModel.selectLanguage(code)
                }
            )
        }
        else -> {
            AppShell(
                isOffline = false,
                lastSyncTime = null,
                roleBadge = authState.role
            )
        }
    }
}
