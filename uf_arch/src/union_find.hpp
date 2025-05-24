#ifndef _UNION_FIND_HPP_
#define _UNION_FIND_HPP_

#include <vector>
#include <set>
#include <algorithm>

#include "types.hpp"
#include "config.hpp"
#include "utils.hpp"

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
    UnionFindDecoder(unsigned int distance, unsigned int rounds, CodeType codeType, int initParallelParam=1, int growParallelParam=1, int earlyStoppingParam=-1);
    ~UnionFindDecoder();

    void decode(std::vector<bool>& syndromes);

    void initCluster(std::vector<bool>& syndromes);
    void initializer(std::vector<bool>& syndromes, int offset, int size);

    void grow();
    void grower(std::vector<Edge*> boundaries, int offset, int size);

    void merge(Edge* edge);
    Node* find(Node* node);
    void peel();

    std::vector<Coords3D> get_horizontal_corrections();

    Stats get_stats() { return stats; }

    unsigned int distance;
    unsigned int rounds;
    CodeType codeType;

    // Node nodes[config::ROUNDS][config::NODES_ROWS][config::NODES_COLS];
    // Edge edge_support[config::ROUNDS][config::EDGES_ROWS][config::EDGES_COLS];
    // Edge vertical_edge_support[config::ROUNDS][config::NODES_ROWS][config::NODES_COLS];

    inline unsigned int getNodeRows() { return getNodeRowsByCodeAndDistance(codeType, distance); }
    inline unsigned int getNodeCols() { return getNodeColsByCodeAndDistance(codeType, distance); }
    inline unsigned int getEdgeRows() { return getEdgeRowsByCodeAndDistance(codeType, distance); }
    inline unsigned int getEdgeCols() { return getEdgeColsByCodeAndDistance(codeType, distance); }

    Node* nodes;
    Edge* edge_support;
    Edge* vertical_edge_support;

private:
    std::set<Node*> odd_clusters;
    std::vector<Edge*> union_list;

    unsigned int max_grown_count = 0;

    int initParallelParam;
    int growParallelParam;
    int earlyStoppingParam;

    Stats stats;

    void peelLeaf(Edge* edge);
};

#endif