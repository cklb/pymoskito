/** @file Controller.h
 * This file includes the base controller implementation for the two tank system.
 *
 */
#ifndef CONTROLLER_H
#define CONTROLLER_H

#include <math.h>

/**
 * @brief Base controller class that can used to derived a P, PI, PD or PID controller.
 */
class Controller {
public:
    /**
     * @brief Method that sets the gain value of the proportional part
     *
     * @param gain value of the proportional part
     */
    void setKp(const double &dKp) { this->dKp = dKp; }

    /**
     * @brief Method that sets the time value of the integral part
     *
     * @param time value of the integral part
     */
    void setTi(const double &dTi) { this->dTi = dTi; }

    /**
     * @brief Method that sets the time value of the derivation part
     *
     * @param time value of the derivation part
     */
    void setTd(const double &dTd) { this->dTd = dTd; }

    /**
     * @brief Method that returns the current sample time of the controller
     *
     * @return the current sample time of the controller
     */
    double getSampleTime() const { return dSampleTime; }

    /**
     * method the computes the controller output of the current time step for the given input value and setpoint
     *
     * @param current input value
     * @param current setpoint
     * @return controller output in the range of min and max output
     */
    virtual double compute(const double &dCurInput,
                           const double &dCurSetpoint) = 0;

    /**
     * @ brief Method that sets the initial values of the PID controller and resets the integral and last error part to zero
     *
     * @param Gain value for the proportional part
     * @param Time value for the integral part
     * @param Time value for the derivation part
     * @param Mininal value for the calculated output
     * @param Maximal value for the calculated output
     * @param Sample time of the controller
     */
    virtual void create(const double &dKp,
                        const double &dTi,
                        const double &dTd,
                        const double &dOutputMin,
                        const double &dOutputMax,
                        const double &dSampleTime) = 0;

    /**
     * @brief Method that resets the integral and last error part to zero
     */
    virtual void reset() = 0;

protected:
    // properties
    double dKp = 1.0;               ///< Gain value for the proportional part
    double dTi = 1.0;               ///< Time value for the integral part
    double dTd = 1.0;               ///< Time value for the derivation part
    double dOutputMin = -255.0;     ///< Mininal value for the calculated output
    double dOutputMax = 255.0;      ///< Maximal value for the calculated output
    double dSampleTime = 0.0;       ///< Sample time of the controller
};

#endif // CONTROLLER_H
