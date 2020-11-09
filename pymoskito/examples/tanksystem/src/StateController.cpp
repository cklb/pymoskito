/** @file StateController.cpp
 * This file includes a state controller implementation for the two tank system.
 *
 */
#include "StateController.h"


double StateController::compute(double *dCurInput,
                                double *dCurSetpoint) {
    double dError = dCurSetpoint - dCurInput;

    this->dOut = this->dGain[0] * dError[0] + this->dGain[1] * dError[1];

    // Apply limit to output value
    if (this->dOut > this->dOutputMax)
        this->dOut = this->dOutputMax;
    else if (this->dOut < this->dOutputMin)
        this->dOut = this->dOutputMin;

    return this->dOut;
}
