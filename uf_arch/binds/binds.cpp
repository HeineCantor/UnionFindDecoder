#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "../src/union_find.hpp"

namespace py = pybind11;

PYBIND11_MODULE(uf_arch, m)
{
    m.doc() = "Union-Find decoder bindings"; // Optional module docstring

    py::class_<Stats>(m, "Stats")
        .def(py::init<>())
        .def_readwrite("num_grow_merge_iters", &Stats::num_grow_merge_iters)
        .def_readwrite("boundaries_per_iter", &Stats::boundaries_per_iter)
        .def_readwrite("merges_per_iter", &Stats::merges_per_iter)
        .def_readwrite("odd_clusters_per_iter", &Stats::odd_clusters_per_iter);

    py::class_<UnionFindDecoder>(m, "UnionFindDecoder")
        .def(py::init<int, int>())
        .def("decode", &UnionFindDecoder::decode)
        .def("initCluster", &UnionFindDecoder::initCluster)
        .def("grow", &UnionFindDecoder::grow)
        .def("get_stats", &UnionFindDecoder::get_stats);
}