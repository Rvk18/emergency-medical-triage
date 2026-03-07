package com.medtriage.app.ui

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.medtriage.app.data.preferences.UserPreferences
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class AppViewModel @Inject constructor(
    private val userPreferences: UserPreferences
) : ViewModel() {

    val darkTheme = userPreferences.darkTheme
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), false)

    fun setDarkTheme(dark: Boolean) {
        viewModelScope.launch {
            userPreferences.setDarkTheme(dark)
        }
    }
}
