/** @file Controller.h
 * This file includes the different observer implementations for the two tank system.
 *
 */
#ifndef HIGHGAINOBSERVER_H
#define HIGHGAINOBSERVER_H

#include <math.h>
#include <vector>
#include <iterator>
#include "Observer.h"

#define M_G 9.81
#define sign(a) ( ( (a) < 0 )  ?  -1   : ( (a) > 0 ) )

/**
 * @brief Class that implements a High Gain Observer.
 */
class HighGainObserver : public Observer {
private:
    double dGain[2];
    double dAT1;
    double dAT2;
    double dAS1;
    double dAS2;
    double dKu;
    double dUA0;
    double dOut[2];
    double dSampleTime;

public:
    /// Constructor of the High Gain observer
    HighGainObserver() {}

    /// Destructor of the High Gain observer
    ~HighGainObserver() {}

    void create(const double &dAT1,
                const double &dAT2,
                const double &dAS1,
                const double &dAS2,
                const double &dKu,
                const double &dUA0,
                const double &dSampleTime);

    /**
     * Sets the initial state
     * @param dInitialState
     */
    void setInitialState(std::vector<double> dInitialState) {
        for (int i = 0; i < 2; i++) {
            this->dOut[i] = dInitialState[i];
        }
    }

    /**
     * Sets the observation gain
     * @param dGain
     */
    void setGain(std::vector<double> dGain) {
        for (int i = 0; i < 2; i++) {
            this->dGain[i] = dGain[i];
        }
    }

    /**
     * Computes the observer output at current time step for the given tank 1 height and the voltage of the
     * pump with the euler method
     *
     * @param tank 1 height
     * @param voltage of the pump
     * @return observed values for tank 1 and 2 height
     */
    std::vector<double> compute(const double &dhT1,
                                const double &dUA);

};

#endif // OBSERVER_H
