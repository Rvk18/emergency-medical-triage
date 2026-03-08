package com.medtriage.app.data.auth

import com.medtriage.app.data.network.ApiConfig
import com.medtriage.app.data.network.CognitoApi
import com.medtriage.app.data.network.CognitoAuthRequestDto
import com.medtriage.app.data.preferences.UserPreferences
import kotlinx.coroutines.flow.first
import retrofit2.HttpException
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class AuthRepository @Inject constructor(
    private val userPreferences: UserPreferences,
    private val cognitoApi: CognitoApi
) {
    suspend fun isLoggedIn(): Boolean = userPreferences.authToken.first() != null

    suspend fun getSessionRole(): String = userPreferences.userRole.first() ?: "Healthcare Worker"

    suspend fun login(emailOrPhone: String, password: String): Result<Unit> {
        if (emailOrPhone.isBlank() || password.isBlank()) {
            return Result.failure(IllegalArgumentException("Email and password required"))
        }
        return try {
            val request = CognitoAuthRequestDto(
                AuthFlow = "USER_PASSWORD_AUTH",
                ClientId = ApiConfig.COGNITO_CLIENT_ID,
                AuthParameters = mapOf(
                    "USERNAME" to emailOrPhone.trim(),
                    "PASSWORD" to password
                )
            )
            val response = cognitoApi.initiateAuth(request = request)
            val result = response.AuthenticationResult
            if (result != null) {
                userPreferences.setAuthToken(result.IdToken)
                userPreferences.setRefreshToken(result.RefreshToken)
                Result.success(Unit)
            } else {
                Result.failure(IllegalArgumentException(
                    response.ChallengeName ?: "Sign-in failed. Complete any required challenge (e.g. new password)."
                ))
            }
        } catch (e: HttpException) {
            val message = e.response()?.errorBody()?.string()?.let { body ->
                parseCognitoError(body) ?: "Invalid email or password"
            } ?: "Invalid email or password"
            Result.failure(IllegalArgumentException(message, e))
        } catch (e: Exception) {
            Result.failure(IllegalArgumentException("Login failed: ${e.message ?: "Check network"}", e))
        }
    }

    private fun parseCognitoError(json: String): String? {
        return try {
            Regex(""""message"\s*:\s*"([^"]+)"""").find(json)?.groupValues?.get(1)
                ?.replace("\\\"", "\"")
        } catch (_: Exception) {
            null
        }
    }

    /**
     * Refresh Id Token using stored RefreshToken (e.g. after 401).
     * On success stores new IdToken; on failure caller should re-prompt sign-in.
     */
    suspend fun refreshToken(): Result<Unit> {
        val refresh = userPreferences.refreshToken.first() ?: return Result.failure(IllegalArgumentException("No refresh token"))
        if (refresh.isBlank()) return Result.failure(IllegalArgumentException("No refresh token"))
        return try {
            val request = CognitoAuthRequestDto(
                AuthFlow = "REFRESH_TOKEN_AUTH",
                ClientId = ApiConfig.COGNITO_CLIENT_ID,
                AuthParameters = mapOf("REFRESH_TOKEN" to refresh)
            )
            val response = cognitoApi.initiateAuth(request = request)
            val result = response.AuthenticationResult
            if (result != null) {
                userPreferences.setAuthToken(result.IdToken)
                result.RefreshToken?.let { userPreferences.setRefreshToken(it) }
                Result.success(Unit)
            } else {
                Result.failure(IllegalArgumentException("Refresh failed"))
            }
        } catch (e: Exception) {
            Result.failure(IllegalArgumentException("Refresh failed: ${e.message}", e))
        }
    }

    suspend fun validateSession(): Boolean {
        val token = userPreferences.authToken.first() ?: return false
        return token.isNotBlank()
    }

    suspend fun logout() {
        userPreferences.clearSession()
    }
}
