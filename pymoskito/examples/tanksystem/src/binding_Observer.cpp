#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "Observer.h"

namespace py = pybind11;

PYBIND11_MODULE(Observer, m) {
    m.doc() = "Binding for Observer";

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
                          const double &>());
}
