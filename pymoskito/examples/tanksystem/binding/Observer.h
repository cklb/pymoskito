/** @file Controller.h
 * This file includes the different observer implementations for the two tank system.
 *
 * Copyright (c) 2018 IACE
 */
#ifndef OBSERVER_H
#define OBSERVER_H

#include <math.h>

#define M_G 9.81

/**
 * @brief Base observer class that can used to derived a Luenberger Observer.
 */
class Observer
{
public:
    // methods
    /**
     * @brief Method that sets the gain
     *
     * @param time value of the derivation part
     */
    void setGain(const double& dTd) { this->dTd = dTd; }
    /**
     * @brief Method that returns the current sample time of the controller
     *
     * @return the current sample time of the controller
     */
    double getSampleTime() const { return dSampleTime; }

    /**
     * method the computs the observer output of the current time step for the given input and output value
     *
     * @param current input value
     * @param current output value
     * @return controller output in the range of min and max output
     */
    virtual double compute(const double& dCurInput,
                           const double& dCurOutput) = 0;

    /**
     * @ brief Method that sets the initial values of the PID controller and resets the integral and last error part to zero
     *
     * @param Gain value for the observer
     * @param Sample time of the controller
     */
	virtual void create(const double& dGain,
                        const double& dSampleTime) = 0;

    /**
     * @brief Method that resets the integral and last error part to zero
     */
    virtual void reset() = 0;

protected:
    // properties
    double* dGain = 0;               ///< Time value for the derivation part
    double dSampleTime = 0.0;        ///< Sample time of the observer
    double* dOutput = 0;             ///< Output of the observer
};

/**
 * @brief Class that is derived from the Controller class and implements a High Gain Observer.
 */
class HighGainObserver : public Observer
{
public:
    /// Constructor of the PID controller
    HighGainObserver() {}
    /// Destructor of the PID controller
    ~HighGainObserver() {}

	void create(const double& dGain,
                const double& dSampleTime);

    void reset();

	double compute(const double& dCurInput,
                   const double& dCurOutput);

};


#endif // OBSERVER_H