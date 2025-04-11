#ifndef _TYPES_HPP_
#define _TYPES_HPP_

#include <vector>

#define BORDER_ID -1
#define INVALID_ID -2

enum EdgeState {
    UNGROWN = 0,
    HALF_GROWN = 1,
    GROWN = 2,

    PEELED = -1,
    MATCHED = -2,
};

struct Edge {
    EdgeState state;

    int nodeA_id = INVALID_ID;
    int nodeB_id = INVALID_ID;
};

struct Node {
    int id;
    int root_id;
    bool syndrome;
    unsigned int ancilla_count;
    unsigned int syndrome_count; 
    bool on_border;

    std::vector<Edge*> boundary;
};

#endif