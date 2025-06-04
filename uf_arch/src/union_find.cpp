#include "union_find.hpp"

UnionFindDecoder::UnionFindDecoder(unsigned int distance, unsigned int rounds, CodeType codeType, int initParallelParam, int growParallelParam, int earlyStoppingParam)
{
    this->initParallelParam = initParallelParam;
    this->growParallelParam = growParallelParam;
    this->earlyStoppingParam = earlyStoppingParam;

    this->distance = distance;
    this->rounds = rounds;
    this->codeType = codeType;

    this->nodes = new Node[rounds * getNodeRows() * getNodeCols()];
    this->edge_support = new Edge[rounds * getEdgeRows() * getEdgeCols()];
    this->vertical_edge_support = new Edge[rounds * getNodeRows() * getNodeCols()];
}

UnionFindDecoder::~UnionFindDecoder()
{
    // Free the allocated memory for nodes, edge_support, and vertical_edge_support
    delete[] nodes;
    delete[] edge_support;
    delete[] vertical_edge_support;
}

void UnionFindDecoder::decode(std::vector<bool>& syndromes)
{
    stats.clear();

    // Initialize the union-find data structure
    initCluster(syndromes);

    unsigned int grow_merge_iters = 0;

    // Grow&Merge Loop
    while (odd_clusters.size())
    {
        if (earlyStoppingParam >= 0 && grow_merge_iters >= earlyStoppingParam)
            break;

        grow_merge_iters++;
        stats.odd_clusters_per_iter.push_back(odd_clusters.size());
        
        auto boundary_sum = 0;
        for (auto cluster : odd_clusters)
            boundary_sum += cluster->boundary.size();
        stats.boundaries_per_iter.push_back(boundary_sum);

        grow();

        unsigned int num_merges = 0;
        for (auto edge : union_list)
        {
            num_merges++;
            merge(edge);
        }

        stats.merges_per_iter.push_back(num_merges);
    }

    stats.num_grow_merge_iters = grow_merge_iters;

    // Perform peeling
    peel();
}

/*
    The initCluster function initializes the union-find data structure
    for the given syndromes. It sets up multiple initalizers based on the
    parallel parameter. Each initializer is responsible for a specific
    portion of the syndromes.

    @param syndromes A vector of booleans representing the syndromes.
*/
void UnionFindDecoder::initCluster(std::vector<bool>& syndromes)
{
    int globalSize = rounds * getNodeRows() * getNodeCols();

    // If the parallel parameter is greater than the global size, we just use less parallel resources.
    if (initParallelParam > globalSize)
        initParallelParam = globalSize;

    int localSize = globalSize / initParallelParam;

    for (int i = 0; i < initParallelParam - 1; i++)
        initializer(syndromes, i*localSize, localSize);

    // The last initializer
    initializer(syndromes, localSize*(initParallelParam-1), globalSize - localSize*(initParallelParam-1));
}

/*
    The initializer function sets up the union-find data structure
    for the given syndromes. It initializes the nodes and edges, and
    sets up the clusters based on the syndromes.

    TODO: erasure init

    @param syndromes A vector of booleans representing the syndromes.
    @param offset The offset to start initializing from.
*/
void UnionFindDecoder::initializer(std::vector<bool>& syndromes, int offset, int size)
{
    for (int i = 0; i < size; i++)
    {
        // Row number is periodic on rounds (rows*cols = total number of nodes in a round)
        auto nodeRow = ((offset + i) % (getNodeRows() * getNodeCols())) / getNodeCols();

        // Column number is periodic on rows
        auto nodeCol = (offset + i) % getNodeCols();

        // Round number is integer division of index and total number of nodes in a round
        auto round = (offset + i) / (getNodeCols() * getNodeRows());

        auto node = &nodes[round * getNodeRows() * getNodeCols() + nodeRow * getNodeCols() + nodeCol];

        // Setting node propertied        
        node->coords = std::make_tuple(round, nodeRow, nodeCol);
        node->root_coords = std::make_tuple(round, nodeRow, nodeCol);
        node->syndrome = syndromes[offset + i];
        node->ancilla_count = 1;
        node->syndrome_count = syndromes[offset + i] ? 1 : 0;
        node->on_border = false;

        // Boundaries from previous decoding shots are cleared
        node->boundary.clear();

        // If the node is a syndrome, it is added to the odd clusters
        if (syndromes[offset + i])
            odd_clusters.insert(node);

        // Setting edge properties
        /*
            Here, each node sets its neighboring edges.

            The edges nodeA and nodeB coordinates are connected to the current node,
            with the convention that nodeA is the one with the lower row coordinate,
            thus each node sets only one between nodeA and nodeB coordinates.

            The only exception is the edges that are on the border of the lattice, 
            which are set to BORDER_ID.
        */

        // Bottom edges
        
        // Bottom edges have "same" row coordinate
        // Bottom edges come in couple for each node, so we need to double the column coordinate
        auto edgeRow = nodeRow;
        auto edgeCol = 2*nodeCol;
        
        // Bottom edges only exist if the node is not on the last row
        if (nodeRow < getNodeRows() - 1)
        {
            // Bottom left

            // For odd rows, the first edge is no bottom edge for any REAL syndrome
            if (nodeRow % 2 == 1)
                edgeCol++;

            auto bottomLeftEdge = &edge_support[round * getEdgeRows() * getEdgeCols() + edgeRow * getEdgeCols() + edgeCol];

            bottomLeftEdge->state = 0;
            bottomLeftEdge->nodeA_coords = node->coords;

            if (nodeRow % 2 == 0 && nodeCol == 0)
                bottomLeftEdge->nodeB_coords = BORDER_ID;
            node->boundary.push_back(bottomLeftEdge);

            // Bottom right
            edgeCol++;

            auto bottomRightEdge = &edge_support[round * getEdgeRows() * getEdgeCols() + edgeRow * getEdgeCols() + edgeCol];

            bottomRightEdge->state = 0;
            bottomRightEdge->nodeA_coords = node->coords;

            if (nodeRow % 2 == 1 && nodeCol == getNodeCols() - 1)
                bottomRightEdge->nodeB_coords = BORDER_ID;
            node->boundary.push_back(bottomRightEdge);
        }

        // Top edges

        // Top edges have a decreased row coordinate
        // Top edges come in couple for each node, so we need to double the column coordinate
        edgeRow = nodeRow - 1;
        edgeCol = 2*nodeCol;

        // Top edges only exist if the node is not on the first row
        if (nodeRow > 0)
        {
            // Top left
            if (nodeRow % 2 == 1)
                edgeCol++;

            auto topLeftEdge = &edge_support[round * getEdgeRows() * getEdgeCols() + edgeRow * getEdgeCols() + edgeCol];

            topLeftEdge->state = 0;
            topLeftEdge->nodeB_coords = node->coords;

            if (nodeRow % 2 == 0 && nodeCol == 0)
                topLeftEdge->nodeA_coords = BORDER_ID;
            node->boundary.push_back(topLeftEdge);

            // Top right
            edgeCol++;

            auto topRightEdge = &edge_support[round * getEdgeRows() * getEdgeCols() + edgeRow * getEdgeCols() + edgeCol];

            topRightEdge->state = 0;
            topRightEdge->nodeB_coords = node->coords;
            
            if (nodeRow % 2 == 1 && nodeCol == getNodeCols() - 1)
                topRightEdge->nodeA_coords = BORDER_ID;
            node->boundary.push_back(topRightEdge);
        }

        // Between rounds edges (vertical edges)
        /*
            Vertical edges connect the current node with the one with same
            row and column coordinates in the previous round.

            In this sense, each node sets only one vertical edge, the one
            connecting with its previous self.
        */
        if (round > 0)
        {
            auto lowerVerticalEdge = &vertical_edge_support[(round - 1) * getNodeRows() * getNodeCols() + nodeRow * getNodeCols() + nodeCol];
            auto lowerNode = &nodes[(round-1) * getNodeRows() * getNodeCols() + nodeRow * getNodeCols() + nodeCol];

            lowerVerticalEdge->state = 0;
            lowerVerticalEdge->nodeA_coords = node->coords;
            lowerVerticalEdge->nodeB_coords = lowerNode->coords;
            node->boundary.push_back(lowerVerticalEdge);
            
            //lowerNode->boundary.push_back(lowerVerticalEdge);
        }

        if (round < rounds -1)
        {
            auto upperVerticalEdge = &vertical_edge_support[round * getNodeRows() * getNodeCols() + nodeRow * getNodeCols() + nodeCol];

            node->boundary.push_back(upperVerticalEdge);
        }

        // Copy boundary into original boundary
        node->original_boundary.clear();
        for (auto edge : node->boundary)
            node->original_boundary.push_back(edge);
    }
}

/*
    The find function is used to find the root of a node in the union-find
    data structure. It uses path compression to optimize the search process.

    @param node The node whose root is to be found.
    @return A pointer to the root node.
*/
Node* UnionFindDecoder::find(Node* node)
{
    auto round = std::get<0>(node->coords);
    auto rowCoord = std::get<1>(node->coords);
    auto colCoord = std::get<2>(node->coords);

    auto rootRound = std::get<0>(node->root_coords);
    auto rootRowCoord = std::get<1>(node->root_coords);
    auto rootColCoord = std::get<2>(node->root_coords);

    if (rowCoord != rootRowCoord || colCoord != rootColCoord || round != rootRound)
        node->root_coords = find(&nodes[rootRound * getNodeRows() * getNodeCols() + rootRowCoord * getNodeCols() + rootColCoord])->root_coords;

    rootRound = std::get<0>(node->root_coords);
    rootRowCoord = std::get<1>(node->root_coords);
    rootColCoord = std::get<2>(node->root_coords);

    return &nodes[rootRound * getNodeRows() * getNodeCols() + rootRowCoord * getNodeCols() + rootColCoord];
}

/*
    The merge function merges two clusters in the union-find data structure.
    It updates the root coordinates, syndrome count, ancilla count, and boundary
    of the clusters. It also handles the case where the clusters are on the border.

    Additionally, if an edge is found to be a cycle in a cluster, it is peeled off
    to enhance the future Peeling Algorithm.

    @param edge The edge that connects the two clusters to be merged.
*/
void UnionFindDecoder::merge(Edge* edge)
{
    Node* rootA;
    Node* rootB;

    auto nodeA_round = std::get<0>(edge->nodeA_coords);
    auto nodeA_row = std::get<1>(edge->nodeA_coords);
    auto nodeA_col = std::get<2>(edge->nodeA_coords);

    auto nodeB_round = std::get<0>(edge->nodeB_coords);
    auto nodeB_row = std::get<1>(edge->nodeB_coords);
    auto nodeB_col = std::get<2>(edge->nodeB_coords);

    max_grown_count += 1;

    if (edge->nodeA_coords == BORDER_ID)
    {
        rootB = find(&nodes[nodeB_round * getNodeRows() * getNodeCols() + nodeB_row * getNodeCols() + nodeB_col]);

        // if B is already on border, we are making a cycle
        if (config::DYNAMIC_CYCLE_PEEL && rootB->on_border)
        {
            edge->state = PEELED;
            max_grown_count -= 1;
        }

        rootB->on_border = true;
        odd_clusters.erase(rootB);
    }
    else if (edge->nodeB_coords == BORDER_ID)
    {
        rootA = find(&nodes[nodeA_round * getNodeRows() * getNodeCols() + nodeA_row * getNodeCols() + nodeA_col]);

        // if A is already on border, we are making a cycle
        if (config::DYNAMIC_CYCLE_PEEL && rootA->on_border)
        {
            edge->state = PEELED;
            max_grown_count -= 1;
        }

        rootA->on_border = true;
        odd_clusters.erase(rootA);
    }
    else
    {
        rootA = find(&nodes[nodeA_round * getNodeRows() * getNodeCols() + nodeA_row * getNodeCols() + nodeA_col]);
        rootB = find(&nodes[nodeB_round * getNodeRows() * getNodeCols() + nodeB_row * getNodeCols() + nodeB_col]);
    
        if (rootA != rootB && !(config::DYNAMIC_CYCLE_PEEL && rootA->on_border && rootB->on_border))
        {
            rootA->boundary.erase(std::remove(rootA->boundary.begin(), rootA->boundary.end(), edge), rootA->boundary.end());
            rootB->boundary.erase(std::remove(rootB->boundary.begin(), rootB->boundary.end(), edge), rootB->boundary.end());

            if (rootA->ancilla_count < rootB->ancilla_count)
                std::swap(rootA, rootB);
    
            rootB->root_coords = rootA->root_coords;
            rootA->syndrome_count += rootB->syndrome_count;
            rootA->ancilla_count += rootB->ancilla_count;
            rootA->boundary.insert(rootA->boundary.end(), rootB->boundary.begin(), rootB->boundary.end());
            rootA->on_border |= rootB->on_border;

            odd_clusters.erase(rootB);

            if (rootA->syndrome_count % 2 == 0 || rootA->on_border)
                odd_clusters.erase(rootA);
            else
                odd_clusters.insert(rootA);
        }
        else if (config::DYNAMIC_CYCLE_PEEL) // Dynamically removing cycles
        {
            edge->state = PEELED;
            max_grown_count -= 1;
        }
    }   
}

/*
    The grow function iteratively grows the clusters in the union-find
    data structure. It updates the state of the boundary edges.

    TODO: maybe we can build leaves LUT support here

    Even clusters, in codes with boundaries, are also clusters that
    touched the border.
*/
void UnionFindDecoder::grow()
{
    union_list.clear();

    std::vector<Edge*> boundaries;

    for (auto cluster : odd_clusters)
        boundaries.insert(boundaries.end(), cluster->boundary.begin(), cluster->boundary.end());

    if (growParallelParam > boundaries.size())
        growParallelParam = boundaries.size();

    int localSize = boundaries.size() / growParallelParam;

    for (int i = 0; i < growParallelParam - 1; i++)
        grower(boundaries, i*localSize, localSize);

    // The last grower
    grower(boundaries, localSize*(growParallelParam-1), boundaries.size() - localSize*(growParallelParam-1));
}

// TODO: grower -> boundary_grower
void UnionFindDecoder::grower(std::vector<Edge*> boundaries, int offset, int size)
{
    for (int i = 0; i < size; i++)
    {
        auto edge = boundaries[offset + i];

        if (edge->state != MAX_GROWN)
        {
            edge->state += 1;

            if (edge->state == MAX_GROWN)
                union_list.push_back(edge);
        }
    }
}

void UnionFindDecoder::peel()
{
    while (max_grown_count)
    {
        for (int i = 0; i < rounds * getEdgeRows() * getEdgeCols(); i++)
        {
            auto edge = &edge_support[i];

            if (edge->state == MAX_GROWN)
                peelLeaf(edge);
        }

        for (int i = 0; i < (rounds-1) * getNodeRows() * getNodeCols(); i++)
        {
            auto edge = &vertical_edge_support[i];

            if (edge->state == MAX_GROWN)
                peelLeaf(edge);
        }
    }
}

void UnionFindDecoder::peelLeaf(Edge* edge)
{
    if (edge->state != MAX_GROWN)
        return;

    if (edge->nodeA_coords == BORDER_ID)
    {
        auto otherNode = &nodes[std::get<0>(edge->nodeB_coords) * getNodeRows() * getNodeCols() + std::get<1>(edge->nodeB_coords) * getNodeCols() + std::get<2>(edge->nodeB_coords)];
        
        // if the non-border node is not a leaf, return, as border leaves should be peeled after the non-border ones
        if (std::count_if(otherNode->original_boundary.begin(), otherNode->original_boundary.end(), [](Edge* edge) { return edge->state == MAX_GROWN; }) != 1)
            return;

        if (otherNode->syndrome)
        {
            otherNode->syndrome ^= true;
            edge->state = MATCHED;
        } else
            edge->state = PEELED;
        
        max_grown_count -= 1;

        return;
    }

    if (edge->nodeB_coords == BORDER_ID)
    {
        auto otherNode = &nodes[std::get<0>(edge->nodeA_coords) * getNodeRows() * getNodeCols() + std::get<1>(edge->nodeA_coords) * getNodeCols() + std::get<2>(edge->nodeA_coords)];
        
        // if the non-border node is not a leaf, return, as border leaves should be peeled after the non-border ones
        if (std::count_if(otherNode->original_boundary.begin(), otherNode->original_boundary.end(), [](Edge* edge) { return edge->state == MAX_GROWN; }) != 1)
            return;
        
        if (otherNode->syndrome)
        {
            otherNode->syndrome ^= true;
            edge->state = MATCHED;
        } else
            edge->state = PEELED;

        max_grown_count -= 1;

        return;
    }

    auto nodeA_round = std::get<0>(edge->nodeA_coords);
    auto nodeA_row = std::get<1>(edge->nodeA_coords);
    auto nodeA_col = std::get<2>(edge->nodeA_coords);

    auto nodeB_round = std::get<0>(edge->nodeB_coords);
    auto nodeB_row = std::get<1>(edge->nodeB_coords);
    auto nodeB_col = std::get<2>(edge->nodeB_coords);

    auto nodeA = &nodes[nodeA_round * getNodeRows() * getNodeCols() + nodeA_row * getNodeCols() + nodeA_col];
    auto nodeB = &nodes[nodeB_round * getNodeRows() * getNodeCols() + nodeB_row * getNodeCols() + nodeB_col];

    // if only one edge in original_boundary is MAX_GROWN, then it is a leaf
    if (std::count_if(nodeA->original_boundary.begin(), nodeA->original_boundary.end(), [](Edge* edge) { return edge->state == MAX_GROWN; }) == 1)
    {
        if (nodeA->syndrome)
        {
            nodeA->syndrome ^= true;
            nodeB->syndrome ^= true;
            edge->state = MATCHED;
        } else
            edge->state = PEELED;

        max_grown_count -= 1;
    }
    else if (std::count_if(nodeB->original_boundary.begin(), nodeB->original_boundary.end(), [](Edge* edge) { return edge->state == MAX_GROWN; }) == 1)
    {
        if (nodeB->syndrome)
        {
            nodeA->syndrome ^= true;
            nodeB->syndrome ^= true;
            edge->state = MATCHED;
        } else
            edge->state = PEELED;

        max_grown_count -= 1;
    }
}

std::vector<Coords3D> UnionFindDecoder::get_horizontal_corrections()
{
    std::vector<Coords3D> corrections;

    for (int i = 0; i < rounds * getEdgeRows() * getEdgeCols(); i++)
    {
        if (edge_support[i].state != MATCHED)
            continue;

        auto round = i / (getEdgeRows() * getEdgeCols());
        auto row = (i % (getEdgeRows() * getEdgeCols())) / getEdgeCols();
        auto col = i % getEdgeCols();

        Coords3D coords = std::make_tuple(round, row, col);
        corrections.push_back(coords);
    }
    
    return corrections;
}