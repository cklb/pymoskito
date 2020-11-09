/** @file StateController.h
 * This file includes a state controller implementation for the two tank system.
 *
 */
#ifndef STATECONTROLLER_H
#define STATECONTROLLER_H

#include <math.h>
#include "Controller.h"


/**
 * @brief Class that is derived from the Controller class and implements a PID controller.
 */
class StateController : public Controller {
public:
    /**
     * @ brief Constructor that sets the initial values of the state controller.
     *
     * @param dGains array of gains
     * @param dPreFiler value of the pre filter
     * @param Mininal value for the calculated output
     * @param Maximal value for the calculated output
     */
    StateController(const double &dGains,
                    const double &dPreFiler,
                    const double &dOutputMin,
                    const double &dOutputMax) {
        this->dOutputMin = dOutputMin;
        this->dOutputMax = dOutputMax;

        this->dPreFiler = dPreFiler;

//        for (int i = 0; i < 2; ++i) {
//            this->dGains[i] = dGains[i];
//        }
    }

    /// Destructor of the state controller
    ~StateController() {}

    double compute(double *dCurInput,
                   double *dCurSetpoint) override;

};

#endif // STATECONTROLLER_H
