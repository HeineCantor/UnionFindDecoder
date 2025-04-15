#include <iostream>
#include <vector>
#include <set>
#include <chrono>
#include <algorithm>

#include "types.hpp"
#include "config.hpp"
#include "utils.hpp"

Node nodes[config::ROUNDS][config::NODES_ROWS][config::NODES_COLS];
Edge edge_support[config::ROUNDS][config::EDGES_ROWS][config::EDGES_COLS];
Edge vertical_edge_support[config::ROUNDS][config::NODES_ROWS][config::NODES_COLS];

std::set<Node*> odd_clusters;
std::vector<Edge*> union_list;

/*
    The init_clusters function initializes the union-find data structure
    for the given syndromes. It sets up the nodes and edges, and populates
    the odd clusters with the initial syndromes.

    TODO: erasure init

    @param syndromes A vector of booleans representing the syndromes.
*/
void init_clusters(std::vector<bool>& syndromes)
{
    for (size_t i = 0; i < syndromes.size(); i++)
    {
        // Row number is periodic on rounds (rows*cols = total number of nodes in a round)
        auto nodeRow = (i % (config::NODES_ROWS * config::NODES_COLS)) / config::NODES_COLS;

        // Column number is periodic on rows
        auto nodeCol = i % config::NODES_COLS;

        // Round number is integer division of index and total number of nodes in a round
        auto round = i / (config::NODES_COLS * config::NODES_ROWS);

        // Setting node properties
        nodes[round][nodeRow][nodeCol].coords = std::make_tuple(round, nodeRow, nodeCol);
        nodes[round][nodeRow][nodeCol].root_coords = std::make_tuple(round, nodeRow, nodeCol);
        nodes[round][nodeRow][nodeCol].syndrome = syndromes[i];
        nodes[round][nodeRow][nodeCol].ancilla_count = 1;
        nodes[round][nodeRow][nodeCol].syndrome_count = syndromes[i] ? 1 : 0;
        nodes[round][nodeRow][nodeCol].on_border = false;

        // Boundaries from previous decoding shots are cleared
        nodes[round][nodeRow][nodeCol].boundary.clear();

        // If the node is a syndrome, it is added to the odd clusters
        if (syndromes[i])
            odd_clusters.insert(&nodes[round][nodeRow][nodeCol]);

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
        if (nodeRow < config::NODES_ROWS - 1)
        {
            // Bottom left

            // For odd rows, the first edge is no bottom edge for any REAL syndrome
            if (nodeRow % 2 == 1)
                edgeCol++;

            edge_support[round][edgeRow][edgeCol].state = UNGROWN;
            edge_support[round][edgeRow][edgeCol].nodeA_coords = nodes[round][nodeRow][nodeCol].coords;
            if (nodeRow % 2 == 0 && nodeCol == 0)
                edge_support[round][edgeRow][edgeCol].nodeB_coords = BORDER_ID;
            nodes[round][nodeRow][nodeCol].boundary.push_back(&edge_support[round][edgeRow][edgeCol]);

            // Bottom right
            edgeCol++;

            edge_support[round][edgeRow][edgeCol].state = UNGROWN;
            edge_support[round][edgeRow][edgeCol].nodeA_coords = nodes[round][nodeRow][nodeCol].coords;
            if (nodeRow % 2 == 1 && nodeCol == config::NODES_COLS - 1)
                edge_support[round][edgeRow][edgeCol].nodeB_coords = BORDER_ID;
            nodes[round][nodeRow][nodeCol].boundary.push_back(&edge_support[round][edgeRow][edgeCol]);
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

            edge_support[round][edgeRow][edgeCol].state = UNGROWN;
            edge_support[round][edgeRow][edgeCol].nodeB_coords = nodes[round][nodeRow][nodeCol].coords;
            if (nodeRow % 2 == 0 && nodeCol == 0)
                edge_support[round][edgeRow][edgeCol].nodeA_coords = BORDER_ID;
            nodes[round][nodeRow][nodeCol].boundary.push_back(&edge_support[round][edgeRow][edgeCol]);

            // Top right
            edgeCol++;

            edge_support[round][edgeRow][edgeCol].state = UNGROWN;
            edge_support[round][edgeRow][edgeCol].nodeB_coords = nodes[round][nodeRow][nodeCol].coords;
            if (nodeRow % 2 == 1 && nodeCol == config::NODES_COLS - 1)
                edge_support[round][edgeRow][edgeCol].nodeA_coords = BORDER_ID;
            nodes[round][nodeRow][nodeCol].boundary.push_back(&edge_support[round][edgeRow][edgeCol]);
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
            vertical_edge_support[round-1][nodeRow][nodeCol].state = UNGROWN;
            vertical_edge_support[round-1][nodeRow][nodeCol].nodeA_coords = nodes[round][nodeRow][nodeCol].coords;
            vertical_edge_support[round-1][nodeRow][nodeCol].nodeB_coords = nodes[round-1][nodeRow][nodeCol].coords;
            nodes[round][nodeRow][nodeCol].boundary.push_back(&vertical_edge_support[round-1][nodeRow][nodeCol]);
            nodes[round-1][nodeRow][nodeCol].boundary.push_back(&vertical_edge_support[round-1][nodeRow][nodeCol]);
        }
    }
}

/*
    The find function is used to find the root of a node in the union-find
    data structure. It uses path compression to optimize the search process.

    @param node The node whose root is to be found.
    @return A pointer to the root node.
*/
Node* find(Node* node)
{
    auto round = std::get<0>(node->coords);
    auto rowCoord = std::get<1>(node->coords);
    auto colCoord = std::get<2>(node->coords);

    auto rootRound = std::get<0>(node->root_coords);
    auto rootRowCoord = std::get<1>(node->root_coords);
    auto rootColCoord = std::get<2>(node->root_coords);

    if (rowCoord != rootRowCoord || colCoord != rootColCoord || round != rootRound)
        node->root_coords = find(&nodes[rootRound][rootRowCoord][rootColCoord])->root_coords;

    rootRound = std::get<0>(node->root_coords);
    rootRowCoord = std::get<1>(node->root_coords);
    rootColCoord = std::get<2>(node->root_coords);

    return &nodes[rootRound][rootRowCoord][rootColCoord];
}

/*
    The merge function merges two clusters in the union-find data structure.
    It updates the root coordinates, syndrome count, ancilla count, and boundary
    of the clusters. It also handles the case where the clusters are on the border.

    Additionally, if an edge is found to be a cycle in a cluster, it is peeled off
    to enhance the future Peeling Algorithm.

    @param edge The edge that connects the two clusters to be merged.
*/
void merge(Edge* edge)
{
    Node* rootA;
    Node* rootB;

    if (edge->nodeA_coords == BORDER_ID)
    {
        rootB = find(&nodes[std::get<0>(edge->nodeB_coords)][std::get<1>(edge->nodeB_coords)][std::get<2>(edge->nodeB_coords)]);

        rootB->on_border = true;
        odd_clusters.erase(rootB);
    }
    else if (edge->nodeB_coords == BORDER_ID)
    {
        rootA = find(&nodes[std::get<0>(edge->nodeA_coords)][std::get<1>(edge->nodeA_coords)][std::get<2>(edge->nodeA_coords)]);

        rootA->on_border = true;
        odd_clusters.erase(rootA);
    }
    else
    {
        rootA = find(&nodes[std::get<0>(edge->nodeA_coords)][std::get<1>(edge->nodeA_coords)][std::get<2>(edge->nodeA_coords)]);
        rootB = find(&nodes[std::get<0>(edge->nodeB_coords)][std::get<1>(edge->nodeB_coords)][std::get<2>(edge->nodeB_coords)]);

        rootA->boundary.erase(std::remove(rootA->boundary.begin(), rootA->boundary.end(), edge), rootA->boundary.end());
        rootB->boundary.erase(std::remove(rootB->boundary.begin(), rootB->boundary.end(), edge), rootB->boundary.end());

        if (rootA != rootB)
        {
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
        else // Dynamically removing cycles
        {
            edge->state = PEELED;
        }
    }   
}

/*
    The grow function iteratively grows the clusters in the union-find
    data structure. It updates the state of the boundary edges and merges 
    the clusters until there are no more odd clusters left.

    Even clusters, in codes with boundaries, are also clusters that
    touched the border.
*/
void grow()
{
    while (odd_clusters.size())
    {
        union_list.clear();

        for (auto cluster : odd_clusters)
        {
            for (auto edge : cluster->boundary)
            {
                if (edge->state != GROWN)
                {
                    edge->state = static_cast<EdgeState>(static_cast<int>(edge->state) + 1);

                    if (edge->state == GROWN)
                        union_list.push_back(edge);
                }
            }
        }

        for (auto& edge : union_list)
            merge(edge);
    }
}

int main()
{
    std::cout << "Code type: " << (config::CODE_TYPE == config::UNROTATED ? "Unrotated" :
        config::CODE_TYPE == config::ROTATED ? "Rotated" :
        config::CODE_TYPE == config::REPETITION ? "Repetition" : "Unknown") << std::endl;
    std::cout << "Code distance: " << config::CODE_DISTANCE << std::endl;
    std::cout << "Rounds: " << config::ROUNDS << std::endl;

    std::cout << "Nodes: " << config::ROUNDS << " x " << config::NODES_ROWS << " x " << config::NODES_COLS << std::endl;
    std::cout << "Edges: " << config::ROUNDS << " x " << config::EDGES_ROWS << " x " << config::EDGES_COLS << std::endl;
    std::cout << "Vertical edges: " << config::ROUNDS << " x " << config::NODES_ROWS << " x " << config::NODES_COLS << std::endl;

    // Testing
    auto syndromes = generate_random_syndrome(config::NODES_COLS * config::NODES_ROWS * config::ROUNDS, 0.01);

    std::cout << "Syndromes: ";
    for (auto s : syndromes)
        std::cout << (s ? "1" : "0");
    std::cout << std::endl;

    auto start = std::chrono::high_resolution_clock::now();

    init_clusters(syndromes);
    grow();

    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start).count();
    
    //print_supports(nodes, edge_support);
    print_edge_support_matrix(edge_support);
    print_vertical_edge_support_matrix(vertical_edge_support);

    std::cout << "Time taken: " << duration << " microseconds" << std::endl;

    return 0;
}