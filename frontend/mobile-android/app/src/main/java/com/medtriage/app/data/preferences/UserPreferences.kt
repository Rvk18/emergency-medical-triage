package com.medtriage.app.data.preferences

import android.content.Context
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import javax.inject.Inject
import javax.inject.Singleton

private val Context.dataStore: DataStore<Preferences> by preferencesDataStore(name = "user_prefs")

@Singleton
class UserPreferences @Inject constructor(
    @ApplicationContext private val context: Context
) {
    private val authTokenKey = stringPreferencesKey("auth_token")
    private val selectedLanguageKey = stringPreferencesKey("selected_language")
    private val userRoleKey = stringPreferencesKey("user_role")

    val authToken: Flow<String?> = context.dataStore.data.map { prefs ->
        prefs[authTokenKey]
    }

    val selectedLanguage: Flow<String?> = context.dataStore.data.map { prefs ->
        prefs[selectedLanguageKey]
    }

    val userRole: Flow<String?> = context.dataStore.data.map { prefs ->
        prefs[userRoleKey]
    }

    suspend fun setAuthToken(token: String?) {
        context.dataStore.edit { prefs ->
            if (token != null) prefs[authTokenKey] = token
            else prefs.remove(authTokenKey)
        }
    }

    suspend fun setSelectedLanguage(languageCode: String) {
        context.dataStore.edit { prefs ->
            prefs[selectedLanguageKey] = languageCode
        }
    }

    suspend fun setUserRole(role: String) {
        context.dataStore.edit { prefs ->
            prefs[userRoleKey] = role
        }
    }

    suspend fun clearSession() {
        context.dataStore.edit { prefs ->
            prefs.remove(authTokenKey)
            prefs.remove(userRoleKey)
        }
    }
}
