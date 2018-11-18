#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "Observer.h"

namespace py = pybind11;

PYBIND11_MODULE(Observer, m)
{
    m.doc() = "Binding of a High Gain Observer";

    py::class_<HighGainObserver> (m, "HighGainObserver")
    .def(py::init())
    .def("create", &HighGainObserver::create, "Create the observer with all needed constants and initialize the output vector")
    .def("compute", &HighGainObserver::compute, "Calculates the observer output")
    .def("setGain", &HighGainObserver::setGain)
    .def("setInitialState", &HighGainObserver::setInitialState);
}