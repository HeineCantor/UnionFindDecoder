#ifndef _UTILS_HPP_
#define _UTILS_HPP_

#include <iostream>
#include <vector>
#include <map>

#include "types.hpp"

inline void print_coords(Coords3D coords)
{
    std::cout << "(" << std::get<0>(coords) << ", " << std::get<1>(coords) << ", " << std::get<2>(coords) << ")";
}

inline unsigned int getNodeRowsByCodeAndDistance(CodeType codeType, unsigned int distance) {
    return codeType == CodeType::UNROTATED ? distance
        : codeType == CodeType::ROTATED ? distance + 1
        : codeType == CodeType::REPETITION ? 1
        : 0;
}

inline unsigned int getNodeColsByCodeAndDistance(CodeType codeType, unsigned int distance) {
    return codeType == CodeType::UNROTATED ? distance - 1
        : codeType == CodeType::ROTATED ? (distance - 1) / 2
        : codeType == CodeType::REPETITION ? distance - 1
        : 0;
}

inline unsigned int getEdgeRowsByCodeAndDistance(CodeType codeType, unsigned int distance) {
    return codeType == CodeType::UNROTATED ? distance * 2 - 1
        : codeType == CodeType::ROTATED ? distance
        : codeType == CodeType::REPETITION ? 1
        : 0;
}

inline unsigned int getEdgeColsByCodeAndDistance(CodeType codeType, unsigned int distance) {
    return codeType == CodeType::UNROTATED ? distance
        : codeType == CodeType::ROTATED ? distance
        : codeType == CodeType::REPETITION ? distance
        : 0;
}

void print_supports(Node* nodes, Edge* edge_support, unsigned int distance, unsigned int rounds, CodeType codeType);
void print_edge_support_matrix(Edge* edge_support, unsigned int rounds, CodeType codeType, unsigned int distance);
void print_vertical_edge_support_matrix(Edge* vertical_edge_support, unsigned int rounds, CodeType codeType, unsigned int distance);
std::vector<bool> generate_random_syndrome(int size, float probability, int seed = -1);
std::map<std::string, EdgeState> get_erasure_map(Edge* edge_support, Edge* vertical_edge_support, unsigned int rounds, CodeType codeType, unsigned int distance);

#endif