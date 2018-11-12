/** @file Controller.h
 * This file includes the different observer implementations for the two tank system.
 *
 * Copyright (c) 2018 IACE
 */
#ifndef OBSERVER_H
#define OBSERVER_H

#include <math.h>

#define M_G 9.81
#define sign(a) ( ( (a) < 0 )  ?  -1   : ( (a) > 0 ) )

/**
 * @brief Class that implements a High Gain Observer.
 */
class HighGainObserver
{
public:
    /// Constructor of the High Gain observer
    HighGainObserver() {}
    /// Destructor of the High Gain observer
    ~HighGainObserver() {}

	void create(const double& dInitialState,
                const double& dGain,
                const double& dAT1,
                const double& dAT2,
                const double& dhT1,
                const double& dhT2,
                const double& dAS1,
                const double& dAS2,
                const double& dKu,
                const double& dUA0,
                const double& dSampleTime,
                const int& iSize);

    void reset();

	double* compute(const double& dhT1,
                    const double& dUA);

private:
    double* dGain;
    double dAT1;
    double dAT2;
    double dhT1;
    double dhT2;
    double dAS1;
    double dAS2;
    double dKu;
    double dUA0;
    double* dOut;
    double dSampleTime;
    int iSize;
};


#endif // OBSERVER_H