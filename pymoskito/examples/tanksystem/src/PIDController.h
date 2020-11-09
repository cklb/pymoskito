/** @file PIDController.h
 * This file includes a PID controller implementation for the two tank system.
 *
 */
#ifndef PIDCONTROLLER_H
#define PIDCONTROLLER_H

#include <math.h>
#include "Controller.h"


/**
 * @brief Class that is derived from the Controller class and implements a PID controller.
 */
class PIDController : public Controller {
private:
    double dIntegral = 0;   ///< Value of the integral part
    double dLastError = 0;  ///< Value of error from the last time step

public:
    /**
     * @ brief Constructor that sets the initial values of the PID controller and resets the integral and last error
     * part to zero.
     *
     * @param dKp Gain value for the proportional part
     * @param dTi Time value for the integral part
     * @param dTd Time value for the derivation part
     * @param dOutputMin Mininal value for the calculated output
     * @param dOutputMax Maximal value for the calculated output
     * @param dSampleTime Sample time of the controller
     */
    PIDController(const double &dKp,
                  const double &dTi,
                  const double &dTd,
                  const double &dOutputMin,
                  const double &dOutputMax,
                  const double &dSampleTime) {
        this->dKp = dKp;
        this->dTi = dTi;
        this->dTd = dTd;
        this->dOutputMin = dOutputMin;
        this->dOutputMax = dOutputMax;

        this->dSampleTime = dSampleTime;

        this->dIntegral = 0.0;
        this->dLastError = 0.0;
    }

    /// Destructor of the PID controller
    ~PIDController() {}

    double compute(double *dCurInput,
                   double *dCurSetpoint) override;

};

#endif // PIDCONTROLLER_H
