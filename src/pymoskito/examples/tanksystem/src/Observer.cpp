/** @file Observer.cpp
 * This file includes the high gain observer implementations for the two tank system with the water level of tank 2
 * as measurement value.
 */
#include "Observer.h"

std::vector<double> HighGainObserver::compute(const double &dhT2,
                                              const double &dUa) {

    // compute rhs
    double dx1 = 0;
    if (this->dOut[0] <= this->dhT) {
           dx1 += this->dK / this->dAT1 * dUa;
    }
    if (this->dOut[0] >= 0) {
           dx1 -= this->da1 * sqrt(this->dOut[0] + this->dhV);
    }
    double dx2 = 0;
    if (this->dOut[1] <= this->dhT) {
           dx2 -= this->da1 * sqrt(this->dOut[0] + this->dhV);
    }
    if (this->dOut[0] >= 0) {
           dx2 -= this->da2 * sqrt(this->dOut[1] + this->dhV);
    }

    // compute euler step with correction term
    double dError = this->dOut[1] - dhT2;
    this->dOut[0] += this->dSampleTime * (dx1 + this->dGain[0] * dError);
    this->dOut[1] += this->dSampleTime * (dx1 + this->dGain[1] * dError);

    // clamp state values
    if (this->dOut[0] <= 0) {
        this->dOut[0] = 0;
    }
    if (this->dOut[1] <= 0) {
        this->dOut[1] = 0;
    }

    std::vector<double> dOut(std::begin(this->dOut), std::end(this->dOut));
    return dOut;
}
