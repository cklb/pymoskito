/** @file Controller.cpp
 * This file includes the PID and state controller implementation for the two tank system.
 *
 */
#include "Controller.h"


double PIDController::compute(double *dCurInput,
                              double *dCurSetpoint) {
    double dError = dCurSetpoint[0] - dCurInput[0];

    double dPartP = dError;

    double dPartI = 0;
    if (this->dTi != 0) {
        if (this->dOutputMin < this->dOut && this->dOut < this->dOutputMax) {
            this->dIntegral += this->dSampleTime * (dError + this->dLastError) * 0.5;
        }

        dPartI = this->dTi * this->dIntegral;
    }

    double dPartD = 0;
    if (this->dTd != 0) {
        dPartD = this->dTd * (dError * dLastError) / this->dSampleTime;
    }

    if (this->dKp != 0) {
        this->dOut = dKp * (dPartP + dPartI + dPartD);
    }

    // Apply limit to output value
    if (this->dOut > this->dOutputMax)
        this->dOut = this->dOutputMax;
    else if (this->dOut < this->dOutputMin)
        this->dOut = this->dOutputMin;

    // Keep track of some variables for next execution
    this->dLastError = dError;

    return this->dOut;
}


double StateController::compute(double *dCurInput,
                                double *dCurSetpoint) {
    this->dOut = 0;
    for (int i = 0; i < 2; ++i) {
        double dError = dCurSetpoint[i] - dCurInput[i];
        this->dOut += this->dGains[i] * dError;
    }

    // Apply limit to output value
    if (this->dOut > this->dOutputMax)
        this->dOut = this->dOutputMax;
    else if (this->dOut < this->dOutputMin)
        this->dOut = this->dOutputMin;

    return this->dOut;
}