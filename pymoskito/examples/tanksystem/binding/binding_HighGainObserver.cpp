#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "HighGainObserver.h"

namespace py = pybind11;

PYBIND11_MODULE(HighGainObserver, m) {
    m.doc() = "Binding of a High Gain Observer";

    py::class_<Observer>(m, "Observer")
            .def("setGain", &Observer::setGain)
            .def("setInitialState", &Observer::setInitialState)
            .def("compute", &Observer::compute,
                 "Calculates the observer output");

    py::class_<HighGainObserver, Observer>(m, "HighGainObserver")
            .def(py::init<const double &,
                          const double &,
                          const double &,
                          const double &,
                          const double &,
                          const double &,
                          const double &>());
}
