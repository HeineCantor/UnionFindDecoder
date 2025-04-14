#ifndef _TYPES_HPP_
#define _TYPES_HPP_

#include <vector>
#include <tuple>

#define BORDER_ID std::make_tuple(-1, -1)
#define INVALID_ID std::make_tuple(-2, -2)

typedef std::tuple<int, int> Coords2D;

enum EdgeState {
    UNGROWN = 0,
    HALF_GROWN = 1,
    GROWN = 2,

    PEELED = -1,
    MATCHED = -2,
};

struct Edge {
    EdgeState state;

    Coords2D nodeA_coords = INVALID_ID;
    Coords2D nodeB_coords = INVALID_ID;
};

struct Node {
    Coords2D coords;
    Coords2D root_coords;
    bool syndrome;
    unsigned int ancilla_count;
    unsigned int syndrome_count; 
    bool on_border;

    std::vector<Edge*> boundary;
};

#endif