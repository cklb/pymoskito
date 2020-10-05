/** @file HighGainObserver.cpp
 * This file includes the high gain observer implementations for the two tank system with the water level of tank 1
 * as measurement value.
 */
#include "HighGainObserver.h"

std::vector<double> HighGainObserver::compute(const double &dhT1,
                                              const double &dUA) {
    double du = 0.0;

    double da1 = this->dAS1 * sqrt(2 * M_G / (pow(this->dAT1, 2) - pow(this->dAS1, 2)));
    double da2 = this->dAS2 * sqrt(2 * M_G / (pow(this->dAT2, 2) - pow(this->dAS2, 2)));

    if (dUA >= this->dUA0) {
        du = dUA - this->dUA0;
    }

    this->dOut[0] += this->dSampleTime *
                     (-da1 * sign(this->dOut[0]) * sqrt(fabs(this->dOut[0])) + this->dKu / this->dAT1 * du +
                      this->dGain[0] * (this->dOut[0] - dhT1));
    this->dOut[1] += this->dSampleTime * (-da2 * sign(this->dOut[1]) * sqrt(fabs(this->dOut[1])) +
                                          da1 * sign(this->dOut[0]) * sqrt(fabs(this->dOut[0])) * this->dAT1 /
                                          this->dAT2 + this->dGain[1] * (this->dOut[0] - dhT1));


    std::vector<double> dOut(std::begin(this->dOut), std::end(this->dOut));
    return dOut;
}
