/** @file Controller.h
 * This file includes the different observer implementations for the two tank system.
 *
 * Copyright (c) 2018 IACE
 */
#ifndef OBSERVER_H
#define OBSERVER_H

#include <math.h>

#if !defined(__AVR__)
    #include <vector>
    #include <iterator>
#endif

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

	void create(const double& dAT1,
                const double& dAT2,
                const double& dhT1,
                const double& dhT2,
                const double& dAS1,
                const double& dAS2,
                const double& dKu,
                const double& dUA0,
                const double& dSampleTime);

#if !defined(__AVR__)
    void setInitialState(std::vector<double> dInitialState) {
#else
    void setInitialState(double dInitialState[2]) {
#endif
        for (int i = 0; i < 2; i++)
        {
            this->dOut[i] = dInitialState[i];
        }
    }

#if !defined(__AVR__)
    void setGain(std::vector<double> dGain) {
#else
    void setGain(double dGain[2]) {
#endif
        for (int i = 0; i < 2; i++)
        {
            this->dGain[i] = dGain[i];
        }
    }

#if !defined(__AVR__)
    std::vector<double> compute(const double& dhT1,
                                  const double& dUA);
#else
    double* compute(const double& dhT1,
                    const double& dUA);
#endif

private:
    double dGain[2];
    double dAT1;
    double dAT2;
    double dhT1;
    double dhT2;
    double dAS1;
    double dAS2;
    double dKu;
    double dUA0;
    double dOut[2];
    double dSampleTime;
};


#endif // OBSERVER_H