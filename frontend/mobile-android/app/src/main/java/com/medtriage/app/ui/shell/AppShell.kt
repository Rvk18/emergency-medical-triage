package com.medtriage.app.ui.shell

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.Place
import androidx.compose.material.icons.filled.Menu
import androidx.compose.material.icons.filled.Person
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import com.medtriage.app.ui.components.CriticalBanner
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.navigation.NavDestination
import androidx.navigation.NavDestination.Companion.hierarchy
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import com.medtriage.app.ui.components.OfflineBanner
import com.medtriage.app.ui.components.SyncStatus
import com.medtriage.app.ui.components.SyncStatusIndicator
import com.medtriage.app.ui.navigation.NavRoutes
import com.medtriage.app.ui.dashboard.DashboardFlowScreen
import com.medtriage.app.ui.hospitals.HospitalsFlowScreen
import com.medtriage.app.ui.patient.NearbyHospitalsScreen
import com.medtriage.app.ui.patient.PatientDashboardScreen
import com.medtriage.app.ui.patient.PatientEmergencyRequestScreen
import com.medtriage.app.ui.screens.MoreScreen
import com.medtriage.app.ui.triage.TriageFlowScreen
import com.medtriage.app.ui.theme.Spacing

data class BottomNavItem(
    val route: String,
    val label: String,
    val icon: ImageVector
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AppShell(
    navController: NavHostController = rememberNavController(),
    isOffline: Boolean = false,
    lastSyncTime: String? = null,
    syncStatus: SyncStatus = SyncStatus.Synced,
    selectedLangCode: String = "en",
    roleBadge: String = "Healthcare Worker",
    userRole: String = "healthcare_worker",
    onLogout: () -> Unit = {},
    showCriticalBanner: Boolean = false,
    criticalBannerMessage: String? = null
) {
    val navBackStackEntry = navController.currentBackStackEntryAsState()
    val currentDestination = navBackStackEntry.value?.destination

    val bottomNavItems = if (userRole == "patient") {
        listOf(
            BottomNavItem(NavRoutes.PatientDashboard, "Dashboard", Icons.Default.Person),
            BottomNavItem(NavRoutes.Hospitals, "Hospitals", Icons.Default.Place),
            BottomNavItem(NavRoutes.More, "More", Icons.Default.Menu)
        )
    } else {
        listOf(
            BottomNavItem(NavRoutes.Triage, "Triage", Icons.Default.Home),
            BottomNavItem(NavRoutes.Hospitals, "Hospitals", Icons.Default.Place),
            BottomNavItem(NavRoutes.Dashboard, "Dashboard", Icons.Default.Person),
            BottomNavItem(NavRoutes.More, "More", Icons.Default.Menu)
        )
    }
    val startDestination = if (userRole == "patient") NavRoutes.PatientDashboard else NavRoutes.Triage

    Scaffold(
        topBar = {
            Column {
                TopAppBar(
                    title = { Text("MedTriage AI") },
                    navigationIcon = {
                        if (navController.previousBackStackEntry != null) {
                            IconButton(onClick = { navController.popBackStack() }) {
                                Icon(
                                    imageVector = Icons.Default.ArrowBack,
                                    contentDescription = "Back"
                                )
                            }
                        }
                    },
                    actions = {
                        SyncStatusIndicator(status = syncStatus, lastSyncTime = lastSyncTime)
                        Text(
                            text = roleBadge,
                            style = androidx.compose.material3.MaterialTheme.typography.labelMedium,
                            modifier = Modifier.padding(end = Spacing.space16)
                        )
                    },
                    colors = TopAppBarDefaults.topAppBarColors(
                        containerColor = androidx.compose.material3.MaterialTheme.colorScheme.primaryContainer,
                        titleContentColor = androidx.compose.material3.MaterialTheme.colorScheme.onPrimaryContainer,
                        navigationIconContentColor = androidx.compose.material3.MaterialTheme.colorScheme.onPrimaryContainer,
                        actionIconContentColor = androidx.compose.material3.MaterialTheme.colorScheme.onPrimaryContainer
                    )
                )
                OfflineBanner(visible = isOffline, lastSyncTime = lastSyncTime)
                if (showCriticalBanner) {
                    CriticalBanner(message = criticalBannerMessage ?: "CRITICAL — Immediate transport. Do not delay.")
                }
            }
        },
        bottomBar = {
            NavigationBar {
                bottomNavItems.forEach { item ->
                    val selected = currentDestination?.isDestination(item.route) == true
                    NavigationBarItem(
                        selected = selected,
                        onClick = {
                            if (!selected) {
                                navController.navigate(item.route) {
                                    popUpTo(navController.graph.startDestinationId) { saveState = true }
                                    launchSingleTop = true
                                    restoreState = true
                                }
                            }
                        },
                        icon = { Icon(item.icon, contentDescription = item.label) },
                        label = { Text(item.label) }
                    )
                }
            }
        }
    ) { paddingValues ->
        NavHost(
            navController = navController,
            startDestination = startDestination,
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
        ) {
            composable(NavRoutes.Triage) {
                TriageFlowScreen(
                    selectedLangCode = selectedLangCode,
                    onProceedToHospitalMatching = {
                        navController.navigate(NavRoutes.Hospitals) {
                            popUpTo(navController.graph.startDestinationId) { saveState = true }
                            launchSingleTop = true
                            restoreState = true
                        }
                    }
                )
            }
            composable(NavRoutes.Hospitals) {
                if (userRole == "patient") {
                    NearbyHospitalsScreen(selectedLangCode = selectedLangCode)
                } else {
                    HospitalsFlowScreen(selectedLangCode = selectedLangCode)
                }
            }
            composable(NavRoutes.Dashboard) {
                DashboardFlowScreen(
                    selectedLangCode = selectedLangCode,
                    onNavigateToTriage = {
                        navController.navigate(NavRoutes.Triage) {
                            popUpTo(navController.graph.startDestinationId) { saveState = true }
                            launchSingleTop = true
                        }
                    },
                    onNavigateToHospitals = {
                        navController.navigate(NavRoutes.Hospitals) {
                            popUpTo(navController.graph.startDestinationId) { saveState = true }
                            launchSingleTop = true
                        }
                    }
                )
            }
            composable(NavRoutes.PatientDashboard) {
                PatientDashboardScreen(
                    selectedLangCode = selectedLangCode,
                    onRequestEmergency = {
                        navController.navigate(NavRoutes.PatientEmergency) {
                            launchSingleTop = true
                        }
                    }
                )
            }
            composable(NavRoutes.PatientEmergency) {
                PatientEmergencyRequestScreen(
                    onBack = { navController.popBackStack() },
                    onSubmit = {
                        // Mock: in real app would call API then navigate back
                        navController.popBackStack()
                    }
                )
            }
            composable(NavRoutes.More) {
                MoreScreen(
                    selectedLangCode = selectedLangCode,
                    onLanguage = { /* TODO: open language selector */ },
                    onLogout = onLogout
                )
            }
        }
    }
}

private fun NavDestination?.isDestination(route: String): Boolean =
    this?.hierarchy?.any { it.route == route } == true
