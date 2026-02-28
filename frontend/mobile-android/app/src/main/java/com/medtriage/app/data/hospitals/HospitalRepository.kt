package com.medtriage.app.data.hospitals

import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.flow
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class HospitalRepository @Inject constructor() {

    fun getMatches(): kotlinx.coroutines.flow.Flow<Result<List<HospitalMatch>>> = flow {
        delay(800)
        emit(Result.success(listOf(
            HospitalMatch("h1", "City General Hospital", 2.5, 8, 12, 50, true, 92),
            HospitalMatch("h2", "Rural Care Center", 5.0, 15, 5, 20, false, 78),
            HospitalMatch("h3", "District Medical College", 7.2, 22, 8, 30, true, 85)
        )))
    }

    fun getRouteSteps(hospitalId: String): kotlinx.coroutines.flow.Flow<Result<List<RouteStep>>> = flow {
        delay(500)
        emit(Result.success(listOf(
            RouteStep("Head north on Main Rd", 500),
            RouteStep("Turn right at Health St", 1200),
            RouteStep("Destination on the left", null)
        )))
    }
}
