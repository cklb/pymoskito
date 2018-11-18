/** @file Controller.cpp
 * This file includes the different observer implementations for the two tank system.
 *
 * Copyright (c) 2018 IACE
 */
#ifndef OBSERVER_CPP
#define OBSERVER_CPP

#include "Observer.h"


void HighGainObserver::create(const double& dAT1,
                              const double& dAT2,
                              const double& dhT1,
                              const double& dhT2,
                              const double& dAS1,
                              const double& dAS2,
                              const double& dKu,
                              const double& dUA0,
                              const double& dSampleTime)
{
    this->dAT1 = dAT1;
    this->dAT2 = dAT2;
    this->dhT1 = dhT1;
    this->dhT2 = dhT2;
    this->dAS1 = dAS1;
    this->dAS2 = dAS2;
    this->dKu = dKu;
    this->dSampleTime = dSampleTime;
}


#if !defined(__AVR__)
    std::vector<double> HighGainObserver::compute(const double& dhT1,
                                                  const double& dUA)
#else
    double* HighGainObserver::compute(const double& dhT1,
                                      const double& dUA)
#endif
{
    double du = 0.0;

    double da1 = this->dAS1 * sqrt(2 * M_G / (pow(this->dAT1, 2) - pow(this->dAS1, 2)));
    double da2 = this->dAS2 * sqrt(2 * M_G / (pow(this->dAT2, 2) - pow(this->dAS2, 2)));

    if (dUA >= this->dUA0)
    {
        du = dUA - this->dUA0;
    }

    this->dOut[0] += this->dSampleTime * (-da1 * sign(this->dOut[0]) * sqrt(fabs(this->dOut[0])) + this->dKu / this->dAT1 * du + this->dGain[0] * (this->dOut[0] - dhT1));
    this->dOut[1] += this->dSampleTime * (-da2 * sign(this->dOut[1]) * sqrt(fabs(this->dOut[1])) + da1 * sign(this->dOut[0]) * sqrt(fabs(this->dOut[0])) * this->dAT1 / this->dAT2 + this->dGain[1] * (this->dOut[0] - dhT1));


#if !defined(__AVR__)
    std::vector<double> dOut(std::begin(this->dOut), std::end(this->dOut));
    return dOut;
#else
    return this->dOut;
#endif
}


#endif // OBSERVER_CPP