/** @file Observer.cpp
 * This file includes the high gain observer implementations for the two tank system with the water level of tank 2
 * as measurement value.
 */
#include "Observer.h"

std::vector<double> HighGainObserver::compute(const double &dhT2,
                                              const double &dUa) {

    double dSgnT = sign(this->dOut[0] - this->dOut[1]);
    double dAbsT = fabs(this->dOut[0] - this->dOut[1]);
    double dError = this->dOut[1] - dhT2;

    this->dOut[0] += this->dSampleTime * (-(this->dAS1 / this->dAT * dSgnT * sqrt(2 * M_G * dAbsT)) +
                                           this->dK / this->dAT * dUa +
                                           this->dGain[0] * dError);
    this->dOut[1] += this->dSampleTime * (this->dAS1 / this->dAT * dSgnT * sqrt(2 * M_G * dAbsT) -
                                          this->dAS2 / this->dAT * sqrt(2 * M_G * this->dOut[1]) +
                                          this->dGain[1] * dError);

    if (this->dOut[0] <= 0) {
        this->dOut[0] = 0;
    }
    if (this->dOut[1] <= 0) {
        this->dOut[1] = 0;
    }

    std::vector<double> dOut(std::begin(this->dOut), std::end(this->dOut));
    return dOut;
}
