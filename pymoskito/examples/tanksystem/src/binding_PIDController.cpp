#include <pybind11/pybind11.h>
#include "../PIDController.h"

namespace py = pybind11;

PYBIND11_MODULE(PIDController, m) {
    m.doc() = "Binding of a PID Controller";

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
}
