/** @file Controller.h
 * This file includes a pid controller implementation for the two tank system.
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
     * @ brief Constructor that sets the initial values of the PID controller and resets the integral and last error part to zero
     *
     * @param Gain value for the proportional part
     * @param Time value for the integral part
     * @param Time value for the derivation part
     * @param Mininal value for the calculated output
     * @param Maximal value for the calculated output
     * @param Sample time of the controller
     */
    PIDController(const double &dKp,
                  const double &dTi,
                  const double &dTd,
                  const double &dOutputMin,
                  const double &dOutputMax,
                  const double &dSampleTime) {
        this->dKp = dKp;
        this->dTd = dTd;
        this->dTi = dTi;
        this->dOutputMin = dOutputMin;
        this->dOutputMax = dOutputMax;

        this->dSampleTime = dSampleTime;

        this->dIntegral = 0.0;
        this->dLastError = 0.0;
    }

    /// Destructor of the PID controller
    ~PIDController() {}

    void reset();

    double compute(const double &dCurInput,
                   const double &dCurSetpoint);

    /**
     * @brief Method that returns the current integral part of the controller
     *
     * @return integral part
     */
    double getIntegral() const { return dIntegral; }

    /**
     * @brief Method that returns the error from the last time step
     *
     * @return error from the last time step
     */
    double getLastError() const { return dLastError; }
};

#endif // PIDCONTROLLER_H
