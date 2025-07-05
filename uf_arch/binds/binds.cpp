#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "../src/union_find.hpp"

namespace py = pybind11;

PYBIND11_MODULE(uf_arch, m)
{
    m.doc() = "Union-Find decoder bindings"; // Optional module docstring

    py::enum_<CodeType>(m, "CodeType")
        .value("UNROTATED", CodeType::UNROTATED)
        .value("ROTATED", CodeType::ROTATED)
        .value("REPETITION", CodeType::REPETITION)
        .export_values();

    py::class_<Stats>(m, "Stats")
        .def(py::init<>())
        .def_readwrite("num_grow_merge_iters", &Stats::num_grow_merge_iters)
        .def_readwrite("boundaries_per_iter", &Stats::boundaries_per_iter)
        .def_readwrite("merges_per_iter", &Stats::merges_per_iter)
        .def_readwrite("odd_clusters_per_iter", &Stats::odd_clusters_per_iter)
        .def_readwrite("num_peeling_iters", &Stats::num_peeling_iters);

    py::class_<UnionFindDecoder>(m, "UnionFindDecoder")
        .def(py::init<unsigned int, unsigned int, CodeType>())
        .def(py::init<unsigned int, unsigned int, CodeType, int, int, int, int>())
        .def("decode", &UnionFindDecoder::decode)
        .def("initCluster", &UnionFindDecoder::initCluster)
        .def("grow", &UnionFindDecoder::grow)
        .def("get_stats", &UnionFindDecoder::get_stats)
        .def("get_horizontal_corrections", &UnionFindDecoder::get_horizontal_corrections);
}