package com.medtriage.app.data.network

import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import javax.inject.Named
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit

@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {

    @Provides
    fun provideOkHttpClient(
        authInterceptor: AuthInterceptor
    ): OkHttpClient = OkHttpClient.Builder()
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .writeTimeout(30, TimeUnit.SECONDS)
        .addInterceptor(authInterceptor)
        .addInterceptor(
            HttpLoggingInterceptor().apply {
                level = HttpLoggingInterceptor.Level.BODY
            }
        )
        .build()

    @Provides
    fun provideRetrofit(okHttpClient: OkHttpClient): Retrofit = Retrofit.Builder()
        .baseUrl(ApiConfig.BASE_URL.ensureTrailingSlash())
        .client(okHttpClient)
        .addConverterFactory(GsonConverterFactory.create())
        .build()

    /** OkHttpClient for Cognito only (no auth header). */
    @Provides
    @Named("cognito")
    fun provideCognitoOkHttpClient(): OkHttpClient = OkHttpClient.Builder()
        .connectTimeout(15, TimeUnit.SECONDS)
        .readTimeout(15, TimeUnit.SECONDS)
        .addInterceptor(
            HttpLoggingInterceptor().apply {
                level = HttpLoggingInterceptor.Level.BODY
            }
        )
        .build()

    @Provides
    @Named("cognito")
    fun provideCognitoRetrofit(@Named("cognito") okHttpClient: OkHttpClient): Retrofit = Retrofit.Builder()
        .baseUrl(ApiConfig.COGNITO_BASE_URL)
        .client(okHttpClient)
        .addConverterFactory(GsonConverterFactory.create())
        .build()

    @Provides
    fun provideCognitoApi(@Named("cognito") retrofit: Retrofit): CognitoApi =
        retrofit.create(CognitoApi::class.java)

    @Provides
    fun provideTriageApi(retrofit: Retrofit): TriageApi = retrofit.create(TriageApi::class.java)

    @Provides
    fun provideHealthApi(retrofit: Retrofit): HealthApi = retrofit.create(HealthApi::class.java)

    @Provides
    fun provideHospitalsApi(retrofit: Retrofit): HospitalsApi = retrofit.create(HospitalsApi::class.java)

    @Provides
    fun provideRouteApi(retrofit: Retrofit): RouteApi = retrofit.create(RouteApi::class.java)

    @Provides
    fun provideRmpLearningApi(retrofit: Retrofit): RmpLearningApi = retrofit.create(RmpLearningApi::class.java)

    private fun String.ensureTrailingSlash(): String = if (endsWith("/")) this else "$this/"
}
