#ifndef _UNION_FIND_HPP_
#define _UNION_FIND_HPP_

#include <vector>
#include <set>
#include <algorithm>

#include "types.hpp"
#include "config.hpp"

// TODO: to test this on Stim, data structures should be dynamic
//       in order to be able to specify the size of the lattice
//       and the number of rounds at each run.

// TODO: PyBindings are necessary to validate in Stim.

class UnionFindDecoder
{
public:
    void decode(std::vector<bool>& syndromes, int initParallelParam=1);

    void initCluster(std::vector<bool>& syndromes, int parallelParam=1);
    void initializer(std::vector<bool>& syndromes, int offset, int size);

    void grow();
    void grower();

    void merge(Edge* edge);
    Node* find(Node* node);
    void peel();

    auto get_edge_support() { return edge_support; }
    auto get_vertical_edge_support() { return vertical_edge_support; }

private:
    Node nodes[config::ROUNDS][config::NODES_ROWS][config::NODES_COLS];
    Edge edge_support[config::ROUNDS][config::EDGES_ROWS][config::EDGES_COLS];
    Edge vertical_edge_support[config::ROUNDS][config::NODES_ROWS][config::NODES_COLS];

    std::set<Node*> odd_clusters;
    std::vector<Edge*> union_list;
};

#endif