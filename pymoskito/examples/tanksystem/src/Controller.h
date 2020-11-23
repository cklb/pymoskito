/** @file Controller.h
 * This file includes the base controller implementation for the two tank system.
 *
 */
#ifndef CONTROLLER_H
#define CONTROLLER_H

#include <math.h>
#include <vector>


/**
 * @brief Base controller class that can used to derived a P, PI, PD, PID or state controller.
 */
class Controller {
protected:
    // properties
    double dKp = 1.0;                       ///< Gain value for the proportional part
    double dTi = 1.0;                       ///< Time value for the integral part
    double dTd = 1.0;                       ///< Time value for the derivation part
    double dOutputMin = -255.0;             ///< Minimal value for the calculated output
    double dOutputMax = 255.0;              ///< Maximal value for the calculated output
    double dSampleTime = 0.0;               ///< Sample time in \f \si{\milli\second} \f
    double dGains[2] = {0.0, 0.0};          ///< Gain values for state controller
    double dLinStates[3] = {0.0, 0.0, 0.0}; ///< Equilibrium states for x1, x2 and uA
    double dPreFiler = 0.0;                 ///< Pre filter value of state controller
    double dOut = 0.0;                      ///< Calculated controller value

public:
    virtual ~Controller() = default;

    /**
     * @brief Method the computes the controller output of the current time step for the given input value and setpoint
     *
     * @param current input value
     * @param current setpoint
     * @return controller output in the range of min and max output
     */
    virtual double compute(std::vector<double> dCurInput,
                           std::vector<double> dCurSetpoint) = 0;
};

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

    double compute(std::vector<double> dCurInput,
                   std::vector<double> dCurSetpoint) override;
};


/**
 * @brief Class that is derived from the Controller class and implements a state controller.
 */
class StateController : public Controller {
public:
    /**
     * @ brief Constructor that sets the initial values of the state controller.
     *
     * @param dGains array of gains
     * @param dPreFiler value of the pre filter
     * @param dLinStates array of equilibrium values for x1, x2 and uA
     * @param Mininal value for the calculated output
     * @param Maximal value for the calculated output
     */
    StateController(std::vector<double> dGains,
                    const double &dPreFiler,
                    std::vector<double> dLinStates,
                    const double &dOutputMin,
                    const double &dOutputMax) {
        this->dOutputMin = dOutputMin;
        this->dOutputMax = dOutputMax;

        this->dPreFiler = dPreFiler;

        for (int i = 0; i < 2; ++i) {
            this->dGains[i] = dGains[i];
        }

        for(int i = 0; i < 3; ++i) {
            this->dLinStates[i] = dLinStates[i];
        }
    }

    /// Destructor of the state controller
    ~StateController() {}

    double compute(std::vector<double> dCurInput,
                   std::vector<double> dCurSetpoint) override;

};

#endif // CONTROLLER_H
