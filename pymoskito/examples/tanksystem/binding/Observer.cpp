/** @file Controller.cpp
 * This file includes the different observer implementations for the two tank system.
 *
 * Copyright (c) 2018 IACE
 */
#ifndef OBSERVER_CPP
#define OBSERVER_CPP

#include "Observer.h"


void HighGainObserver::create(const double& dGain,
                              const double& dSampleTime)
{
    this->dGain = dGain;

	this->dSampleTime = dSampleTime;
}


void LuenbergerObserver::reset()
{
    this->dIntegral = 0.0;
    this->dLastError = 0.0;
}


double LuenbergerObserver::compute(const double& dCurInput,
                              const double& dCurSetpoint)
{
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
    if ((long long) (this->dTi * 1000) == 0LL)
    {
	    dOut = this->dKp * (dError + this->dTd * dDifferential);
    }
    else
    {
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


#endif // OBSERVER_CPP