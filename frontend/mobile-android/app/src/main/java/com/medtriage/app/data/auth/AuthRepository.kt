package com.medtriage.app.data.auth

import com.medtriage.app.data.preferences.UserPreferences
import kotlinx.coroutines.flow.first
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class AuthRepository @Inject constructor(
    private val userPreferences: UserPreferences
) {
    suspend fun isLoggedIn(): Boolean = userPreferences.authToken.first() != null

    suspend fun getSessionRole(): String = userPreferences.userRole.first() ?: "Healthcare Worker"

    suspend fun login(emailOrPhone: String, password: String): Result<Unit> {
        return try {
            // Mock: accept any non-empty credentials; real app would call /auth/login
            if (emailOrPhone.isBlank() || password.isBlank()) {
                Result.failure(IllegalArgumentException("Email/phone and password required"))
            } else {
                userPreferences.setAuthToken("mock_jwt_${System.currentTimeMillis()}")
                userPreferences.setUserRole("Healthcare Worker")
                Result.success(Unit)
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun validateSession(): Boolean {
        val token = userPreferences.authToken.first() ?: return false
        // Mock: consider valid if token exists; real app would call /auth/validate
        return token.isNotBlank()
    }

    suspend fun logout() {
        userPreferences.clearSession()
    }
}
