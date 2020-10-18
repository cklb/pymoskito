/** @file HighGainObserver.cpp
 * This file includes the high gain observer implementations for the two tank system with the water level of tank 1
 * as measurement value.
 */
#include "HighGainObserver.h"

std::vector<double> HighGainObserver::compute(const double &dhT2,
                                              const double &dUa) {
    this->dOut[0] += this->dSampleTime * ( -this->dAS1 / this->dAT * sign(this->dOut[0] - this->dOut[1]) *
                      sqrt(2 * M_G * fabs(this->dOut[0] - this->dOut[1])) + this->dK / this->dAT * du +
                      this->dGain[0] * (this->dOut[0] - dhT2));
    this->dOut[1] += this->dSampleTime * (this->dAS1 / this->dAT * sign(this->dOut[0] - this->dOut[1]) *
                      sqrt(2 * M_G * fabs(this->dOut[0] - this->dOut[1])) +
                      this->dAS2 / this->dAT * sqrt + sqrt(2 * M_G * this->dOut[1]) +
                      this->dGain[0] * (this->dOut[0] - dhT2));

    std::vector<double> dOut(std::begin(this->dOut), std::end(this->dOut));
    return dOut;
}
