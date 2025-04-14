#ifndef _UTILS_HPP_
#define _UTILS_HPP_

#include <iostream>
#include <vector>

#include "types.hpp"
#include "config.hpp"

inline void print_coords(Coords2D coords)
{
    std::cout << "(" << std::get<0>(coords) << ", " << std::get<1>(coords) << ")";
}

void print_supports(Node nodes[config::NODES_ROWS][config::NODES_COLS],
                    Edge edge_support[config::EDGES_ROWS][config::EDGES_COLS])
{
    // Print the nodes
    std::cout << "Syndromes: " << std::endl;
    for (int i = 0; i < config::NODES_ROWS; i++)
    {
        for (int j = 0; j < config::NODES_COLS; j++)
        {
            // Print full node
            std::cout << "Node coords: ";
            print_coords(nodes[i][j].coords);
            std::cout << std::endl;
            
            std::cout << "Root coords (" << std::get<0>(nodes[i][j].root_coords) << ", " << std::get<1>(nodes[i][j].root_coords) << "): ";
            print_coords(nodes[i][j].root_coords);
            std::cout << std::endl;

            std::cout << "Syndrome: " << (nodes[i][j].syndrome ? "true" : "false") << ", ";
            std::cout << "Ancilla count: " << nodes[i][j].ancilla_count << ", ";
            std::cout << "Syndrome count: " << nodes[i][j].syndrome_count << ", ";
            std::cout << "On border: " << (nodes[i][j].on_border ? "true" : "false") << ", ";
            std::cout << "Boundary: ";
            for (auto& edge : nodes[i][j].boundary)
            {
                std::cout << "Edge: ";
                print_coords(edge->nodeA_coords);
                std::cout << "---";
                print_coords(edge->nodeB_coords);
                std::cout << " | ";
            }
            std::cout << std::endl;
        }
        std::cout << std::endl;
    }

    // Print the edges
    std::cout << "Edges: " << std::endl;
    for (int i = 0; i < config::EDGES_ROWS; i++)
    {
        for (int j = 0; j < config::EDGES_COLS; j++)
        {
            // Print full edge
            std::cout << "Edge: ";
            print_coords(edge_support[i][j].nodeA_coords);
            std::cout << "---";
            print_coords(edge_support[i][j].nodeB_coords);
            std::cout << std::endl;
            std::cout << "State: " << edge_support[i][j].state << std::endl;
        }
    }
    std::cout << std::endl;
}

void print_edge_support_matrix(Edge edge_support[config::EDGES_ROWS][config::EDGES_COLS])
{
    std::cout << "Edge support matrix: " << std::endl;
    for (int i = 0; i < config::EDGES_ROWS; i++)
    {
        for (int j = 0; j < config::EDGES_COLS; j++)
        {
            std::cout << edge_support[i][j].state << " ";
        }
        std::cout << std::endl;
    }
}

std::vector<bool> generate_random_syndrome(int size, float probability)
{
    srand(static_cast<unsigned int>(time(0)));

    std::vector<bool> syndrome(size);
    for (int i = 0; i < size; i++)
    {
        syndrome[i] = (rand() / (float)RAND_MAX) < probability;
    }
    return syndrome;
}

#endif