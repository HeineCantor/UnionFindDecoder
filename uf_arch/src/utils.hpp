#ifndef _UTILS_HPP_
#define _UTILS_HPP_

#include <iostream>
#include <vector>
#include <map>

#include "types.hpp"
#include "config.hpp"

inline void print_coords(Coords3D coords)
{
    std::cout << "(" << std::get<0>(coords) << ", " << std::get<1>(coords) << ", " << std::get<2>(coords) << ")";
}

void print_supports(Node nodes[config::ROUNDS][config::NODES_ROWS][config::NODES_COLS],
                    Edge edge_support[config::ROUNDS][config::EDGES_ROWS][config::EDGES_COLS])
{
    // Print the nodes
    for (int r = 0; r < config::ROUNDS; r++)
    {
        std::cout << "Round " << r << ": " << std::endl;
        for (int i = 0; i < config::NODES_ROWS; i++)
        {
            for (int j = 0; j < config::NODES_COLS; j++)
            {
                // Print full node
                std::cout << "Node coords: ";
                print_coords(nodes[r][i][j].coords);
                std::cout << std::endl;
                
                std::cout << "Root coords: ";
                print_coords(nodes[r][i][j].root_coords);
                std::cout << std::endl;

                std::cout << "Syndrome: " << (nodes[r][i][j].syndrome ? "true" : "false") << ", ";
                std::cout << "Ancilla count: " << nodes[r][i][j].ancilla_count << ", ";
                std::cout << "Syndrome count: " << nodes[r][i][j].syndrome_count << ", ";
                std::cout << "On border: " << (nodes[r][i][j].on_border ? "true" : "false") << ", ";
                std::cout << "Boundary: ";
                for (auto& edge : nodes[r][i][j].boundary)
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
                print_coords(edge_support[r][i][j].nodeA_coords);
                std::cout << "---";
                print_coords(edge_support[r][i][j].nodeB_coords);
                std::cout << std::endl;
                std::cout << "State: " << edge_support[r][i][j].state << std::endl;
            }
        }
        std::cout << std::endl;
    }
}

void print_edge_support_matrix(Edge edge_support[config::ROUNDS][config::EDGES_ROWS][config::EDGES_COLS])
{
    std::cout << "Edge support matrix: " << std::endl;
    for (int r = 0; r < config::ROUNDS; r++)
    {
        std::cout << "Round " << r << ": " << std::endl;

        for (int i = 0; i < config::EDGES_ROWS; i++)
        {
            for (int j = 0; j < config::EDGES_COLS; j++)
            {
                std::cout << edge_support[r][i][j].state << " ";
            }
            std::cout << std::endl;
        }
    }
}

void print_vertical_edge_support_matrix(Edge vertical_edge_support[config::ROUNDS][config::NODES_ROWS][config::NODES_COLS])
{
    std::cout << "Vertical edge support matrix: " << std::endl;
    for (int r = 0; r < config::ROUNDS; r++)
    {
        std::cout << "Round " << r << ": " << std::endl;

        for (int i = 0; i < config::NODES_ROWS; i++)
        {
            for (int j = 0; j < config::NODES_COLS; j++)
            {
                std::cout << vertical_edge_support[r][i][j].state << " ";
            }
            std::cout << std::endl;
        }
    }
}

std::vector<bool> generate_random_syndrome(int size, float probability)
{
    srand(42); // Seed the random number generator

    std::vector<bool> syndrome(size);
    for (int i = 0; i < size; i++)
    {
        syndrome[i] = (rand() / (float)RAND_MAX) < probability;
    }
    return syndrome;
}

std::map<std::string, EdgeState> get_erasure_map(Edge edge_support[config::ROUNDS][config::EDGES_ROWS][config::EDGES_COLS],
                                                   Edge vertical_edge_support[config::ROUNDS][config::NODES_ROWS][config::NODES_COLS])
{
    std::map<std::string, EdgeState> erasure_map;

    for (int r = 0; r < config::ROUNDS; r++)
    {
        for (int i = 0; i < config::EDGES_ROWS; i++)
        {
            for (int j = 0; j < config::EDGES_COLS; j++)
            {
                std::string key = "H(" + std::to_string(r) + "," + std::to_string(i) + "," + std::to_string(j) + ")";
                erasure_map[key] = edge_support[r][i][j].state;
            }
        }

        for (int i = 0; i < config::NODES_ROWS; i++)
        {
            for (int j = 0; j < config::NODES_COLS; j++)
            {
                std::string key = "V(" + std::to_string(r) + "," + std::to_string(i) + "," + std::to_string(j) + ")";
                erasure_map[key] = vertical_edge_support[r][i][j].state;
            }
        }
    }

    return erasure_map;
}

#endif