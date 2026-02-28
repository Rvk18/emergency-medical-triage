package com.medtriage.app.ui.shell

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.Place
import androidx.compose.material.icons.filled.Menu
import androidx.compose.material.icons.filled.Person
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.navigation.NavDestination
import androidx.navigation.NavDestination.Companion.hierarchy
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import com.medtriage.app.ui.components.OfflineBanner
import com.medtriage.app.ui.navigation.NavRoutes
import com.medtriage.app.ui.dashboard.DashboardFlowScreen
import com.medtriage.app.ui.hospitals.HospitalsFlowScreen
import com.medtriage.app.ui.screens.MorePlaceholderScreen
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
    roleBadge: String = "Healthcare Worker"
) {
    val navBackStackEntry = navController.currentBackStackEntryAsState()
    val currentDestination = navBackStackEntry.value?.destination

    val bottomNavItems = listOf(
        BottomNavItem(NavRoutes.Triage, "Triage", Icons.Default.Home),
        BottomNavItem(NavRoutes.Hospitals, "Hospitals", Icons.Default.Place),
        BottomNavItem(NavRoutes.Dashboard, "Dashboard", Icons.Default.Person),
        BottomNavItem(NavRoutes.More, "More", Icons.Default.Menu)
    )

    Scaffold(
        topBar = {
            Column {
                TopAppBar(
                    title = { Text("MedTriage AI") },
                    actions = {
                        Text(
                            text = roleBadge,
                            style = androidx.compose.material3.MaterialTheme.typography.labelMedium,
                            modifier = Modifier.padding(end = Spacing.space16)
                        )
                    },
                    colors = TopAppBarDefaults.topAppBarColors(
                        containerColor = androidx.compose.material3.MaterialTheme.colorScheme.primaryContainer,
                        titleContentColor = androidx.compose.material3.MaterialTheme.colorScheme.onPrimaryContainer,
                        actionIconContentColor = androidx.compose.material3.MaterialTheme.colorScheme.onPrimaryContainer
                    )
                )
                OfflineBanner(visible = isOffline, lastSyncTime = lastSyncTime)
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
            startDestination = NavRoutes.Triage,
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
        ) {
            composable(NavRoutes.Triage) {
                TriageFlowScreen(
                    onProceedToHospitalMatching = {
                        navController.navigate(NavRoutes.Hospitals) {
                            popUpTo(navController.graph.startDestinationId) { saveState = true }
                            launchSingleTop = true
                            restoreState = true
                        }
                    }
                )
            }
            composable(NavRoutes.Hospitals) { HospitalsFlowScreen() }
            composable(NavRoutes.Dashboard) {
                DashboardFlowScreen(
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
            composable(NavRoutes.More) { MorePlaceholderScreen() }
        }
    }
}

private fun NavDestination?.isDestination(route: String): Boolean =
    this?.hierarchy?.any { it.route == route } == true
