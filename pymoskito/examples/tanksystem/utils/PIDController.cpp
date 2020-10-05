/** @file PIDController.cpp
 * This file includes a PID controller implementation for the two tank system.
 *
 */
#include "PIDController.h"


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
