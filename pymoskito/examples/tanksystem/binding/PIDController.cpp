/** @file PIDController.cpp
 * This file includes a pid controller implementation for the two tank system.
 *
 */
#ifndef PIDCONTROLLER_CPP
#define PIDCONTROLLER_CPP

#include "PIDController.h"


void PIDController::create(const double &dKp,
                           const double &dTi,
                           const double &dTd,
                           const double &dOutputMin,
                           const double &dOutputMax,
                           const double &dSampleTime) {
    this->dKp = dKp;
    this->dTd = dTd;
    this->dTi = dTi;
    this->dOutputMin = dOutputMin;
    this->dOutputMax = dOutputMax;

    this->dSampleTime = dSampleTime;

    this->dIntegral = 0.0;
    this->dLastError = 0.0;
}


void PIDController::reset() {
    this->dIntegral = 0.0;
    this->dLastError = 0.0;
}


double PIDController::compute(const double &dCurInput,
                              const double &dCurSetpoint) {
    double dError = dCurSetpoint - dCurInput;

    this->dIntegral += (dError + dLastError) * this->dSampleTime;

    if (this->dIntegral > this->dOutputMax)
        this->dIntegral = this->dOutputMax;
    else if (this->dIntegral < this->dOutputMin)
        this->dIntegral = this->dOutputMin;

    // Compute differential part
    double dDifferential = (dError - this->dLastError) / this->dSampleTime;

    // Compute PID output
    double dOut = 0.0;
    if ((long long) (this->dTi * 1000) == 0LL) {
        dOut = this->dKp * (dError + this->dTd * dDifferential);
    } else {
        dOut = this->dKp * (dError +
                            this->dIntegral / (2.0 * this->dTi) +
                            this->dTd * dDifferential);
    }

    // Apply limit to output value
    if (dOut > this->dOutputMax)
        dOut = this->dOutputMax;
    else if (dOut < this->dOutputMin)
        dOut = this->dOutputMin;

    // Keep track of some variables for next execution
    this->dLastError = dError;

    return dOut;
}

#endif // PIDCONTROLLER_CPP
