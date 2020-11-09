#include <pybind11/pybind11.h>
#include "Controller.h"

namespace py = pybind11;

PYBIND11_MODULE(Controller, m) {
    m.doc() = "Binding for Controller";

    py::class_<Controller>(m, "Controller")
            .def("compute", &Controller::compute,
                 "Calculates the control output");

    py::class_<PIDController, Controller>(m, "PIDController")
            .def(py::init<const double &,
                          const double &,
                          const double &,
                          const double &,
                          const double &,
                          const double &>());

    py::class_<StateController, Controller>(m, "StateController")
            .def(py::init<double*,
                          const double &,
                          const double &,
                          const double &>());
}
