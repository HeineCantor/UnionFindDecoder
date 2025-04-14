#include <iostream>
#include <vector>
#include <chrono>
#include <algorithm>

#include "types.hpp"
#include "config.hpp"
#include "utils.hpp"

// TODO: rounds
// TODO: adapt to multiple types of code
Node nodes[config::NODES_ROWS][config::NODES_COLS];
Edge edge_support[config::EDGES_ROWS][config::EDGES_COLS];

std::vector<Node*> odd_clusters;

// TODO: erasure init
void init_clusters(std::vector<bool>& syndromes)
{
    for (size_t i = 0; i < syndromes.size(); i++)
    {
        auto nodeRow = i / config::NODES_COLS;
        auto nodeCol = i % config::NODES_COLS;

        nodes[nodeRow][nodeCol].coords = std::make_tuple(nodeRow, nodeCol);
        nodes[nodeRow][nodeCol].root_coords = std::make_tuple(nodeRow, nodeCol);
        nodes[nodeRow][nodeCol].syndrome = syndromes[i];
        nodes[nodeRow][nodeCol].ancilla_count = 1;
        nodes[nodeRow][nodeCol].syndrome_count = syndromes[i] ? 1 : 0;
        nodes[nodeRow][nodeCol].on_border = false;

        nodes[nodeRow][nodeCol].boundary.clear();

        if (syndromes[i])
            odd_clusters.push_back(&nodes[nodeRow][nodeCol]);

        auto edgeRow = nodeRow;
        auto edgeCol = 2*nodeCol;

        // Bottom edges
        if (nodeRow < config::NODES_ROWS - 1)
        {
            // Bottom left
            if (nodeRow % 2 == 1)
                edgeCol++;

            edge_support[edgeRow][edgeCol].state = UNGROWN;
            edge_support[edgeRow][edgeCol].nodeA_coords = nodes[nodeRow][nodeCol].coords;
            if (nodeRow % 2 == 0 && nodeCol == 0)
                edge_support[edgeRow][edgeCol].nodeB_coords = BORDER_ID;
            nodes[nodeRow][nodeCol].boundary.push_back(&edge_support[edgeRow][edgeCol]);

            // Bottom right
            edgeCol++;

            edge_support[edgeRow][edgeCol].state = UNGROWN;
            edge_support[edgeRow][edgeCol].nodeA_coords = nodes[nodeRow][nodeCol].coords;
            if (nodeRow % 2 == 1 && nodeCol == config::NODES_COLS - 1)
                edge_support[edgeRow][edgeCol].nodeB_coords = BORDER_ID;
            nodes[nodeRow][nodeCol].boundary.push_back(&edge_support[edgeRow][edgeCol]);
        }


        edgeRow = nodeRow - 1;
        edgeCol = 2*nodeCol;

        // Top edges
        if (nodeRow > 0)
        {
            // Top left
            if (nodeRow % 2 == 1)
                edgeCol++;

            edge_support[edgeRow][edgeCol].state = UNGROWN;
            edge_support[edgeRow][edgeCol].nodeB_coords = nodes[nodeRow][nodeCol].coords;
            if (nodeRow % 2 == 0 && nodeCol == 0)
                edge_support[edgeRow][edgeCol].nodeA_coords = BORDER_ID;
            nodes[nodeRow][nodeCol].boundary.push_back(&edge_support[edgeRow][edgeCol]);

            // Top right
            edgeCol++;

            edge_support[edgeRow][edgeCol].state = UNGROWN;
            edge_support[edgeRow][edgeCol].nodeB_coords = nodes[nodeRow][nodeCol].coords;
            if (nodeRow % 2 == 1 && nodeCol == config::NODES_COLS - 1)
                edge_support[edgeRow][edgeCol].nodeA_coords = BORDER_ID;
            nodes[nodeRow][nodeCol].boundary.push_back(&edge_support[edgeRow][edgeCol]);
        }
    }
}

Node* find(Node* node)
{
    auto rowCoord = std::get<0>(node->coords);
    auto colCoord = std::get<1>(node->coords);

    auto rootRowCoord = std::get<0>(node->root_coords);
    auto rootColCoord = std::get<1>(node->root_coords);

    if (rowCoord != rootRowCoord || colCoord != rootColCoord)
        node->root_coords = find(&nodes[rootRowCoord][rootColCoord])->root_coords;

    rootRowCoord = std::get<0>(node->root_coords);
    rootColCoord = std::get<1>(node->root_coords);

    return &nodes[rootRowCoord][rootColCoord];
}

void merge(Edge* edge)
{
    Node* rootA;
    Node* rootB;

    if (edge->nodeA_coords == BORDER_ID)
    {
        rootB = find(&nodes[std::get<0>(edge->nodeB_coords)][std::get<1>(edge->nodeB_coords)]);

        rootB->on_border = true;
        odd_clusters.erase(std::remove(odd_clusters.begin(), odd_clusters.end(), rootB), odd_clusters.end());
    }
    else if (edge->nodeB_coords == BORDER_ID)
    {
        rootA = find(&nodes[std::get<0>(edge->nodeA_coords)][std::get<1>(edge->nodeA_coords)]);

        rootA->on_border = true;
        odd_clusters.erase(std::remove(odd_clusters.begin(), odd_clusters.end(), rootA), odd_clusters.end());
    }
    else
    {
        rootA = find(&nodes[std::get<0>(edge->nodeA_coords)][std::get<1>(edge->nodeA_coords)]);
        rootB = find(&nodes[std::get<0>(edge->nodeB_coords)][std::get<1>(edge->nodeB_coords)]);

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

            odd_clusters.erase(std::remove(odd_clusters.begin(), odd_clusters.end(), rootB), odd_clusters.end());

            if (rootA->syndrome_count % 2 == 0 || rootA->on_border)
                odd_clusters.erase(std::remove(odd_clusters.begin(), odd_clusters.end(), rootA), odd_clusters.end());
        }
        else // Dynamically removing cycles
        {
            edge->state = PEELED;
        }
    }   
}

std::vector<Edge*> union_list;

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

    std::cout << "Nodes: " << config::NODES_ROWS << " x " << config::NODES_COLS << std::endl;
    std::cout << "Edges: " << config::EDGES_ROWS << " x " << config::EDGES_COLS << std::endl;

    // Testing
    auto syndromes = generate_random_syndrome(config::NODES_COLS * config::NODES_ROWS, 0.1);
    // syndromes = std::vector<bool>(config::NODES_COLS * config::NODES_ROWS, false);
    // syndromes[9] = true;
    // syndromes[11] = true;

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

    std::cout << "Time taken: " << duration << " microseconds" << std::endl;

    return 0;
}