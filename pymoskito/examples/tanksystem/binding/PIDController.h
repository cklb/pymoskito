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
    /// Constructor of the PID controller
    PIDController() {}

    /// Destructor of the PID controller
    ~PIDController() {}

    void create(const double &dKp,
                const double &dTi,
                const double &dTd,
                const double &dOutputMin,
                const double &dOutputMax,
                const double &dSampleTime);

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
