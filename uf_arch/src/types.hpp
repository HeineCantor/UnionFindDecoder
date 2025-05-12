#ifndef _TYPES_HPP_
#define _TYPES_HPP_

#include <vector>
#include <tuple>
#include "config.hpp"

#define BORDER_ID std::make_tuple(-1, -1, -1)
#define INVALID_ID std::make_tuple(-2, -2, -2)

typedef std::tuple<int, int, int> Coords3D;
typedef int EdgeState;

const EdgeState MAX_GROWN = 2;
const EdgeState PEELED = -1;
const EdgeState MATCHED = -2;

// TODO: here, we have some opinable choice. We should clarify if
//       edges and nodes in both structures should be saved as
//       with their coordinates or as pointers.

/*
    The Edge struct represents an edge in the support.

    @param state The state of the edge in the union-find data structure. In weighted union-find,
                 the state is used to keep track of the current weight of the edge.
    @param nodeA_coords The coordinates of the first node connected by the edge (by convetion,
                 the node with the lower row coordinate).
    @param nodeB_coords The coordinates of the second node connected by the edge (by convetion,
                 the node with the higher row coordinate).
*/
struct Edge {
    EdgeState state;

    Coords3D nodeA_coords = INVALID_ID;
    Coords3D nodeB_coords = INVALID_ID;
};

/*
    The Node struct represents a node in the support.

    @param coords The coordinates of the node in the lattice (#round, #row, #col).
    @param root_coords The coordinates of the root node in the cluster (#round, #row, #col).
    @param syndrome true if the node itself is as syndrome, false otherwise.
    @param ancilla_count The number of nodes in the cluster represented by the node.
    @param syndrome_count The number of syndromes in the cluster represented by the node.
    @param on_border true if the cluster touches the border of the lattice, false otherwise.
    @param boundary Edge pointers that are on the boundary of the cluster.
*/
struct Node {
    Coords3D coords;
    Coords3D root_coords;
    bool syndrome;
    unsigned int ancilla_count;
    unsigned int syndrome_count; 
    bool on_border;

    std::vector<Edge*> boundary;
};

typedef Edge EdgeSupport[config::ROUNDS][config::EDGES_ROWS][config::EDGES_COLS];
typedef Edge VerticalEdgeSupport[config::ROUNDS][config::NODES_ROWS][config::NODES_COLS];
typedef Node NodeSupport[config::ROUNDS][config::NODES_ROWS][config::NODES_COLS];

#endif