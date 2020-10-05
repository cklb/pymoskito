/** @file HighGainObserver.h
 * This file includes the high gain observer implementation for the two tank system with the water level of tank 1
 * as measurement value.
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
    double dGain[2] = {};   ///< gain values of the observer
    double dAT1;            ///< area of tank 1
    double dAT2;            ///< area of tank 2
    double dAS1;            ///< area of sink 1
    double dAS2;            ///< area of sink 2
    double dKu;             ///< gain value of pump
    double dUA0;            ///< base voltage of pump
    double dOut[2] = {};    ///< observed states respectively water level of tank 1 and 2

public:
    /**
     * @ brief Constructor that sets the initial values of the observer.
     *
     * @param dAT1 area of tank 1
     * @param dAT2 area of tank 2
     * @param dAS1 area of sink 1
     * @param dAS2 area of sink 2
     * @param dKu gain value of pump
     * @param dUA0 base voltage of pump
     * @param dSampleTime sample time in \f \si{\milli\second} \f
     */
    HighGainObserver(const double &dAT1,
                     const double &dAT2,
                     const double &dAS1,
                     const double &dAS2,
                     const double &dKu,
                     const double &dUA0,
                     const double &dSampleTime) {
        this->dAT1 = dAT1;
        this->dAT2 = dAT2;
        this->dAS1 = dAS1;
        this->dAS2 = dAS2;
        this->dKu = dKu;
        this->dUA0 = dUA0;
        this->dSampleTime = dSampleTime;
    }

    /// Destructor of the High Gain observer
    ~HighGainObserver() {}

    /**
     * Sets the initial state.
     * @param dInitialState vector with two starting values for the water levels of tank 1 and 2
     */
    void setInitialState(std::vector<double> dInitialState) {
        for (int i = 0; i < 2; ++i) {
            this->dOut[i] = dInitialState[i];
        }
    }

    /**
     * Sets the observation gain.
     * @param dGain vector with two values for the gains
     */
    void setGain(std::vector<double> dGain) {
        for (int i = 0; i < 2; ++i) {
            this->dGain[i] = dGain[i];
        }
    }

    /**
     * Computes the observer output at current time step for the given tank 1 height and the voltage of the
     * pump with the euler method.
     *
     * @param water level tank 1
     * @param voltage of the pump
     * @return observed water levels of tank 1 and 2
     */
    std::vector<double> compute(const double &dhT1,
                                const double &dUA);

};

#endif // HIGHGAINOBSERVER_H
