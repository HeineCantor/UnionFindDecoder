#include <iostream>

#include "types.hpp"
#include "config.hpp"

// TODO: rounds
// TODO: adapt to multiple types of code
Node nodes[config::NODES_ROWS][config::NODES_COLS];
Edge edge_support[config::EDGES_ROWS][config::EDGES_COLS];

void init_clusters(std::vector<bool>& syndromes)
{
    for (size_t i = 0; i < syndromes.size(); i++)
    {
        auto nodeRow = i / config::NODES_COLS;
        auto nodeCol = i % config::NODES_COLS;

        nodes[nodeRow][nodeCol].id = i;
        nodes[nodeRow][nodeCol].root_id = i;
        nodes[nodeRow][nodeCol].syndrome = syndromes[i];
        nodes[nodeRow][nodeCol].ancilla_count = 1;
        nodes[nodeRow][nodeCol].syndrome_count = syndromes[i] ? 1 : 0;
        nodes[nodeRow][nodeCol].on_border = false;

        nodes[nodeRow][nodeCol].boundary.clear();

        auto edgeRow = nodeRow;
        auto edgeCol = nodeCol;

        // Bottom edges
        if (nodeRow < config::NODES_ROWS - 1)
        {
            // Bottom left
            if (nodeRow % 2 == 1)
                edgeCol++;

            edge_support[edgeRow][edgeCol].state = UNGROWN;
            edge_support[edgeRow][edgeCol].nodeA_id = nodes[nodeRow][nodeCol].id;
            if (nodeRow % 2 == 0 && nodeCol == 0)
                edge_support[edgeRow][edgeCol].nodeB_id = BORDER_ID;
            nodes[nodeRow][nodeCol].boundary.push_back(&edge_support[edgeRow][edgeCol]);

            // Bottom right
            edgeCol++;

            edge_support[edgeRow][edgeCol].state = UNGROWN;
            edge_support[edgeRow][edgeCol].nodeA_id = nodes[nodeRow][nodeCol].id;
            if (nodeRow % 2 == 1 && nodeCol == config::NODES_COLS - 1)
                edge_support[edgeRow][edgeCol].nodeB_id = BORDER_ID;
            nodes[nodeRow][nodeCol].boundary.push_back(&edge_support[edgeRow][edgeCol]);
        }


        edgeRow = nodeRow - 1;
        edgeCol = nodeCol + 1;

        // Top edges
        if (nodeRow > 0)
        {
            // Top left
            if (nodeRow % 2 == 0)
                edgeCol--;

            edge_support[edgeRow][edgeCol].state = UNGROWN;
            edge_support[edgeRow][edgeCol].nodeB_id = nodes[nodeRow][nodeCol].id;
            if (nodeRow % 2 == 0 && nodeCol == 0)
                edge_support[edgeRow][edgeCol].nodeA_id = BORDER_ID;
            nodes[nodeRow][nodeCol].boundary.push_back(&edge_support[edgeRow][edgeCol]);

            // Top right
            edgeCol++;

            edge_support[edgeRow][edgeCol].state = UNGROWN;
            edge_support[edgeRow][edgeCol].nodeB_id = nodes[nodeRow][nodeCol].id;
            if (nodeRow % 2 == 1 && nodeCol == config::NODES_COLS - 1)
                edge_support[edgeRow][edgeCol].nodeA_id = BORDER_ID;
            nodes[nodeRow][nodeCol].boundary.push_back(&edge_support[edgeRow][edgeCol]);
        }
    }
}

void print_supports()
{
    // Print the nodes
    std::cout << "Syndromes: " << std::endl;
    for (int i = 0; i < config::NODES_ROWS; i++)
    {
        for (int j = 0; j < config::NODES_COLS; j++)
        {
            // Print full node
            std::cout << "Node " << nodes[i][j].id << ": ";
            std::cout << "Root ID: " << nodes[i][j].root_id << ", ";
            std::cout << "Syndrome: " << (nodes[i][j].syndrome ? "true" : "false") << ", ";
            std::cout << "Ancilla count: " << nodes[i][j].ancilla_count << ", ";
            std::cout << "Syndrome count: " << nodes[i][j].syndrome_count << ", ";
            std::cout << "On border: " << (nodes[i][j].on_border ? "true" : "false") << ", ";
            std::cout << "Boundary: ";
            for (auto& edge : nodes[i][j].boundary)
            {
                std::cout << "Edge (" << edge->nodeA_id << ", " << edge->nodeB_id << ") ";
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
            std::cout << "Edge (" << edge_support[i][j].nodeA_id << ", " << edge_support[i][j].nodeB_id << "): ";
            std::cout << "State: " << edge_support[i][j].state << std::endl;
        }
    }
    std::cout << std::endl;
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
    std::vector<bool> syndromes = std::vector<bool>(config::NODES_COLS * config::NODES_ROWS, false);
    syndromes[2] = true;

    init_clusters(syndromes);

    print_supports();

    return 0;
}