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

struct Stats
{
    int num_grow_merge_iters = 0;

    std::vector<int> boundaries_per_iter;
    std::vector<int> merges_per_iter;
    std::vector<int> odd_clusters_per_iter;

    void clear()
    {
        num_grow_merge_iters = 0;

        boundaries_per_iter.clear();
        merges_per_iter.clear();
        odd_clusters_per_iter.clear();
    }
};

class UnionFindDecoder
{
public:
    UnionFindDecoder(int initParallelParam=1, int growParallelParam=1);

    void decode(std::vector<bool>& syndromes);

    void initCluster(std::vector<bool>& syndromes);
    void initializer(std::vector<bool>& syndromes, int offset, int size);

    void grow();
    void grower(std::vector<Edge*> boundaries, int offset, int size);

    void merge(Edge* edge);
    Node* find(Node* node);
    void peel();

    Stats get_stats() { return stats; }

    Node nodes[config::ROUNDS][config::NODES_ROWS][config::NODES_COLS];
    Edge edge_support[config::ROUNDS][config::EDGES_ROWS][config::EDGES_COLS];
    Edge vertical_edge_support[config::ROUNDS][config::NODES_ROWS][config::NODES_COLS];

private:
    std::set<Node*> odd_clusters;
    std::vector<Edge*> union_list;

    int initParallelParam;
    int growParallelParam;

    Stats stats;
};

#endif