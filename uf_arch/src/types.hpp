#ifndef _TYPES_HPP_
#define _TYPES_HPP_

#include <vector>
#include <tuple>

#define BORDER_ID std::make_tuple(-1, -1, -1)
#define INVALID_ID std::make_tuple(-2, -2, -2)

typedef std::tuple<int, int, int> Coords3D;
typedef int EdgeState;

const EdgeState MAX_GROWN = 2;
const EdgeState PEELED = -1;
const EdgeState MATCHED = -2;

struct Edge {
    EdgeState state;

    Coords3D nodeA_coords = INVALID_ID;
    Coords3D nodeB_coords = INVALID_ID;
};

struct Node {
    Coords3D coords;
    Coords3D root_coords;
    bool syndrome;
    unsigned int ancilla_count;
    unsigned int syndrome_count; 
    bool on_border;

    std::vector<Edge*> boundary;
};

#endif