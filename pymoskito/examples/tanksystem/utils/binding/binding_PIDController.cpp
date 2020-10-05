#include <pybind11/pybind11.h>
#include "../PIDController.h"

namespace py = pybind11;

PYBIND11_MODULE(PIDController, m) {
    m.doc() = "Binding of a PID Controller";

    py::class_<Controller>(m, "Controller")
            .def("setKp", &Controller::setKp, "Sets the proportional gain")
            .def("setTi", &Controller::setTi, "Sets the integral time")
            .def("setTd", &Controller::setTd, "Sets the derivative time")
            .def("getSampleTime", &Controller::getSampleTime,
                 "Returns the sample time")
            .def("compute", &Controller::compute,
                 "Calculates the control output")
            .def("reset", &Controller::reset,
                 "Resets the integral and last error variable to zero");

    py::class_<PIDController, Controller>(m, "PIDController")
            .def(py::init<const double &,
                          const double &,
                          const double &,
                          const double &,
                          const double &,
                          const double &>())
            .def("getIntegral", &PIDController::getIntegral,
                 "Returns the integral part of the controller")
            .def("getLastError", &PIDController::getLastError,
                 "Returns the the given error element from the last computation");
}
