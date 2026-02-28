package com.medtriage.app.ui.auth

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.medtriage.app.data.auth.AuthRepository
import com.medtriage.app.data.preferences.UserPreferences
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.combine
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch
import javax.inject.Inject

data class AuthUiState(
    val isLoggedIn: Boolean = false,
    val hasLanguageSelected: Boolean = false,
    val role: String = "Healthcare Worker",
    val isLoading: Boolean = true
)

@HiltViewModel
class AuthViewModel @Inject constructor(
    private val authRepository: AuthRepository,
    private val userPreferences: UserPreferences
) : ViewModel() {

    val authState: StateFlow<AuthUiState> = combine(
        userPreferences.authToken.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), null),
        userPreferences.selectedLanguage.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), null),
        userPreferences.userRole.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), null)
    ) { token, language, role ->
        AuthUiState(
            isLoggedIn = !token.isNullOrBlank(),
            hasLanguageSelected = !language.isNullOrBlank(),
            role = role ?: "Healthcare Worker",
            isLoading = false
        )
    }.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), AuthUiState(isLoading = true))

    fun login(emailOrPhone: String, password: String, onResult: (Result<Unit>) -> Unit) {
        viewModelScope.launch {
            onResult(authRepository.login(emailOrPhone, password))
        }
    }

    fun selectLanguage(languageCode: String) {
        viewModelScope.launch {
            userPreferences.setSelectedLanguage(languageCode)
        }
    }

    fun logout() {
        viewModelScope.launch {
            authRepository.logout()
        }
    }
}
