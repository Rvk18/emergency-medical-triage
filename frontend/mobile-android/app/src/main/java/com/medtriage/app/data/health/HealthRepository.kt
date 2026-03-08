package com.medtriage.app.data.health

import com.medtriage.app.data.network.HealthApi
import com.medtriage.app.data.network.HealthResponseDto
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.io.IOException
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class HealthRepository @Inject constructor(
    private val healthApi: HealthApi
) {
    suspend fun checkHealth(): Result<HealthResponseDto> = withContext(Dispatchers.IO) {
        try {
            val response = healthApi.health()
            Result.success(response)
        } catch (e: IOException) {
            Result.failure(IOException("Network error: ${e.message}", e))
        } catch (e: retrofit2.HttpException) {
            Result.failure(IOException("API error ${e.code()}: ${e.response()?.errorBody()?.string()}", e))
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
