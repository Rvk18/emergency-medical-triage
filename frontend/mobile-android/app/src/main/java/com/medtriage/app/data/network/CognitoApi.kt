package com.medtriage.app.data.network

import retrofit2.http.Body
import retrofit2.http.Header
import retrofit2.http.POST

/**
 * Interface into AWS Cognito Identity Provider for getting auth tokens.
 */
interface CognitoApi {

    @POST("/")
    suspend fun initiateAuth(
        @Header("X-Amz-Target") target: String = "AWSCognitoIdentityProviderService.InitiateAuth",
        @Header("Content-Type") contentType: String = "application/x-amz-json-1.1",
        @Body request: CognitoAuthRequestDto
    ): CognitoAuthResponseDto
}

data class CognitoAuthRequestDto(
    val AuthFlow: String = "USER_PASSWORD_AUTH",
    val ClientId: String,
    val AuthParameters: Map<String, String>
)

data class CognitoAuthResponseDto(
    val AuthenticationResult: CognitoAuthResultDto? = null,
    val ChallengeName: String? = null
)

data class CognitoAuthResultDto(
    val AccessToken: String,
    val ExpiresIn: Int,
    val TokenType: String,
    val RefreshToken: String?,
    val IdToken: String
)
