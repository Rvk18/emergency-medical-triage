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
import com.medtriage.app.ui.screens.RoleSelectorScreen
import com.medtriage.app.ui.shell.AppShell

@Composable
fun MedTriageApp(
    authViewModel: AuthViewModel = hiltViewModel(),
    appViewModel: AppViewModel = hiltViewModel()
) {
    val authState by authViewModel.authState.collectAsState()
    val darkTheme by appViewModel.darkTheme.collectAsState(initial = false)

    when {
        authState.isLoading -> {
            Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                CircularProgressIndicator()
            }
        }
        !authState.hasRoleSelected || !authState.hasLanguageSelected -> {
            RoleSelectorScreen(
                darkTheme = darkTheme,
                selectedLangCode = authState.languageCode,
                onDarkThemeChange = appViewModel::setDarkTheme,
                onLanguageSelected = authViewModel::selectLanguage,
                onSelectRole = authViewModel::setUserRole
            )
        }
        !authState.isLoggedIn -> {
            LoginScreen(
                darkTheme = darkTheme,
                onDarkThemeChange = appViewModel::setDarkTheme,
                onLoginSuccess = { },
                onLogin = { email, password, onResult ->
                    authViewModel.login(email, password, onResult)
                },
                onBackToRoleSelection = authViewModel::clearUserRole,
                onSettingsClick = { }
            )
        }
        else -> {
            AppShell(
                isOffline = false,
                lastSyncTime = null,
                roleBadge = if (authState.role == "patient") "Patient" else "Healthcare Worker",
                userRole = authState.role,
                onLogout = authViewModel::logout
            )
        }
    }
}
