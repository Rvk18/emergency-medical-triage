package com.medtriage.app.data.location

import android.content.Context
import android.content.pm.PackageManager
import android.location.Location
import android.location.LocationListener
import android.location.LocationManager
import android.os.Handler
import android.os.Looper
import androidx.core.content.ContextCompat
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import kotlinx.coroutines.suspendCancellableCoroutine
import java.util.concurrent.atomic.AtomicBoolean
import javax.inject.Inject
import javax.inject.Singleton
import kotlin.coroutines.resume
import android.Manifest

/** Result of a location fetch: latitude and longitude from GPS. */
data class LocationResult(
    val latitude: Double,
    val longitude: Double
) {
    fun toPair(): Pair<Double, Double> = latitude to longitude
}

@Singleton
class LocationRepository @Inject constructor(
    @ApplicationContext private val context: Context
) {
    private val locationManager: LocationManager
        get() = context.getSystemService(Context.LOCATION_SERVICE) as LocationManager

    /** Returns true if the app has at least coarse location permission. */
    fun hasLocationPermission(): Boolean =
        ContextCompat.checkSelfPermission(context, Manifest.permission.ACCESS_FINE_LOCATION) == PackageManager.PERMISSION_GRANTED ||
            ContextCompat.checkSelfPermission(context, Manifest.permission.ACCESS_COARSE_LOCATION) == PackageManager.PERMISSION_GRANTED

    /** Returns true if GPS provider is enabled. */
    fun isGpsEnabled(): Boolean =
        try {
            locationManager.isProviderEnabled(LocationManager.GPS_PROVIDER)
        } catch (_: Exception) {
            false
        }

    /**
     * Gets the current location: tries GPS first, then network (cell/wifi) if GPS is disabled.
     * Falls back to last known (GPS or network) on timeout.
     */
    suspend fun getCurrentLocation(): Result<LocationResult> = withContext(Dispatchers.Main.immediate) {
        if (!hasLocationPermission()) {
            return@withContext Result.failure(SecurityException("Location permission not granted"))
        }
        val provider = if (isGpsEnabled()) LocationManager.GPS_PROVIDER else LocationManager.NETWORK_PROVIDER
        suspendCancellableCoroutine { cont ->
            val resumed = AtomicBoolean(false)
            fun tryResume(result: Result<LocationResult>) {
                if (resumed.compareAndSet(false, true)) {
                    cont.resume(result)
                }
            }
            val listener = object : LocationListener {
                override fun onLocationChanged(location: Location) {
                    locationManager.removeUpdates(this)
                    tryResume(Result.success(LocationResult(location.latitude, location.longitude)))
                }
                @Deprecated("Deprecated in Java")
                override fun onStatusChanged(provider: String?, status: Int, extras: android.os.Bundle?) {}
                override fun onProviderEnabled(provider: String) {}
                override fun onProviderDisabled(provider: String) {}
            }
            try {
                locationManager.requestSingleUpdate(
                    provider,
                    listener,
                    Looper.getMainLooper()
                )
                cont.invokeOnCancellation {
                    try { locationManager.removeUpdates(listener) } catch (_: SecurityException) {}
                }
                val handler = Handler(Looper.getMainLooper())
                val timeoutRunnable = Runnable {
                    if (!cont.isCancelled) {
                        try { locationManager.removeUpdates(listener) } catch (_: SecurityException) {}
                        val last = getLastKnownLocation()
                        tryResume(
                            if (last != null) Result.success(last)
                            else Result.failure(IllegalStateException("Location unavailable or timed out"))
                        )
                    }
                }
                handler.postDelayed(timeoutRunnable, TIMEOUT_MS)
                cont.invokeOnCancellation { handler.removeCallbacks(timeoutRunnable) }
            } catch (e: SecurityException) {
                tryResume(Result.failure(e))
            }
        }
    }

    /**
     * Last known location: tries GPS first, then network (cell/wifi). Quick, no wait.
     * Network often has a fix when GPS hasn't updated yet.
     */
    fun getLastKnownLocation(): LocationResult? {
        if (!hasLocationPermission()) return null
        return try {
            locationManager.getLastKnownLocation(LocationManager.GPS_PROVIDER)?.let {
                LocationResult(it.latitude, it.longitude)
            } ?: locationManager.getLastKnownLocation(LocationManager.NETWORK_PROVIDER)?.let {
                LocationResult(it.latitude, it.longitude)
            }
        } catch (_: SecurityException) {
            null
        }
    }

    companion object {
        private const val TIMEOUT_MS = 15_000L
    }
}
