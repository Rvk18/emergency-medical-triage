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
        // Mock: accept any non-empty credentials (no backend auth call)
        if (emailOrPhone.isBlank() || password.isBlank()) {
            return Result.failure(IllegalArgumentException("Email/phone and password required"))
        }
        return try {
            userPreferences.setAuthToken("mock_jwt_${System.currentTimeMillis()}")
            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(IllegalArgumentException("Login failed: ${e.message}", e))
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
