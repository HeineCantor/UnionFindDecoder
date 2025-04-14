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

// TODO: erasure init
void init_clusters(std::vector<bool>& syndromes)
{
    for (size_t i = 0; i < syndromes.size(); i++)
    {
        auto nodeRow = (i % (config::NODES_ROWS * config::NODES_COLS)) / config::NODES_COLS;
        auto nodeCol = i % config::NODES_COLS;
        auto round = i / (config::NODES_COLS * config::NODES_ROWS);

        nodes[round][nodeRow][nodeCol].coords = std::make_tuple(round, nodeRow, nodeCol);
        nodes[round][nodeRow][nodeCol].root_coords = std::make_tuple(round, nodeRow, nodeCol);
        nodes[round][nodeRow][nodeCol].syndrome = syndromes[i];
        nodes[round][nodeRow][nodeCol].ancilla_count = 1;
        nodes[round][nodeRow][nodeCol].syndrome_count = syndromes[i] ? 1 : 0;
        nodes[round][nodeRow][nodeCol].on_border = false;

        nodes[round][nodeRow][nodeCol].boundary.clear();

        if (syndromes[i])
            odd_clusters.insert(&nodes[round][nodeRow][nodeCol]);

        auto edgeRow = nodeRow;
        auto edgeCol = 2*nodeCol;

        // Bottom edges
        if (nodeRow < config::NODES_ROWS - 1)
        {
            // Bottom left
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


        edgeRow = nodeRow - 1;
        edgeCol = 2*nodeCol;

        // Top edges
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

        // Between rounds edges
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