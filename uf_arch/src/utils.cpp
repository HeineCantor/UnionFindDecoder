#include "utils.hpp"

void print_supports(Node* nodes, Edge* edge_support, unsigned int distance, unsigned int rounds, CodeType codeType)
{
    auto nodeRows = getNodeRowsByCodeAndDistance(codeType, distance);
    auto nodeCols = getNodeColsByCodeAndDistance(codeType, distance);
    auto edgeRows = getEdgeRowsByCodeAndDistance(codeType, distance);
    auto edgeCols = getEdgeColsByCodeAndDistance(codeType, distance);

    // Print the nodes
    for (auto r = 0; r < rounds; r++)
    {
        std::cout << "Round " << r << ": " << std::endl;
        for (auto i = 0; i < nodeRows; i++)
        {
            for (auto j = 0; j < nodeCols; j++)
            {
                auto node = &nodes[r * nodeRows * nodeCols + i * nodeCols + j];

                // Print full node
                std::cout << "Node coords: ";
                print_coords(node->coords);
                std::cout << std::endl;
                
                std::cout << "Root coords: ";
                print_coords(node->root_coords);
                std::cout << std::endl;

                std::cout << "Syndrome: " << (node->syndrome ? "true" : "false") << ", ";
                std::cout << "Ancilla count: " << node->ancilla_count << ", ";
                std::cout << "Syndrome count: " << node->syndrome_count << ", ";
                std::cout << "On border: " << (node->on_border ? "true" : "false") << ", ";
                std::cout << "Boundary: ";
                for (auto& edge : node->boundary)
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
        for (auto i = 0; i < edgeRows; i++)
        {
            for (auto j = 0; j < edgeCols; j++)
            {
                auto edge = &edge_support[r * edgeRows * edgeCols + i * edgeCols + j];

                // Print full edge
                std::cout << "Edge: ";
                print_coords(edge->nodeA_coords);
                std::cout << "---";
                print_coords(edge->nodeB_coords);
                std::cout << std::endl;
                std::cout << "State: " << edge->state << std::endl;
            }
        }
        std::cout << std::endl;
    }
}

void print_edge_support_matrix(Edge* edge_support, unsigned int rounds, CodeType codeType, unsigned int distance)
{
    auto edgeRows = getEdgeRowsByCodeAndDistance(codeType, distance);
    auto edgeCols = getEdgeColsByCodeAndDistance(codeType, distance);

    std::cout << "Edge support matrix: " << std::endl;
    for (auto r = 0; r < rounds; r++)
    {
        std::cout << "Round " << r << ": " << std::endl;

        for (auto i = 0; i < edgeRows; i++)
        {
            for (auto j = 0; j < edgeCols; j++)
            {
                auto edge = &edge_support[r * edgeRows * edgeCols + i * edgeCols + j];

                std::cout << edge->state << " ";
            }
            std::cout << std::endl;
        }
    }
}

void print_vertical_edge_support_matrix(Edge* vertical_edge_support, unsigned int rounds, CodeType codeType, unsigned int distance)
{
    auto nodeRows = getNodeRowsByCodeAndDistance(codeType, distance);
    auto nodeCols = getNodeColsByCodeAndDistance(codeType, distance);

    std::cout << "Vertical edge support matrix: " << std::endl;
    for (auto r = 0; r < rounds; r++)
    {
        std::cout << "Round " << r << ": " << std::endl;

        for (auto i = 0; i < nodeRows; i++)
        {
            for (auto j = 0; j < nodeCols; j++)
            {
                auto edge = &vertical_edge_support[r * nodeRows * nodeCols + i * nodeCols + j];

                std::cout << edge->state << " ";
            }
            std::cout << std::endl;
        }
    }
}

std::vector<bool> generate_random_syndrome(int size, float probability, int seed)
{
    if (seed == -1)
        std::srand(time(NULL));
    else
        std::srand(seed);

    std::vector<bool> syndrome(size);
    for (int i = 0; i < size; i++)
    {
        syndrome[i] = (std::rand() / (float)RAND_MAX) < probability;
    }
    return syndrome;
}

std::map<std::string, EdgeState> get_erasure_map(Edge* edge_support, Edge* vertical_edge_support, unsigned int rounds, CodeType codeType, unsigned int distance)
{
    std::map<std::string, EdgeState> erasure_map;

    auto edgeRows = getEdgeRowsByCodeAndDistance(codeType, distance);
    auto edgeCols = getEdgeColsByCodeAndDistance(codeType, distance);
    auto nodeRows = getNodeRowsByCodeAndDistance(codeType, distance);
    auto nodeCols = getNodeColsByCodeAndDistance(codeType, distance);

    for (int r = 0; r < rounds; r++)
    {
        for (int i = 0; i < edgeRows; i++)
        {
            for (int j = 0; j < edgeCols; j++)
            {
                auto edge = &edge_support[r * edgeRows * edgeCols + i * edgeCols + j];

                std::string key = "H(" + std::to_string(r) + "," + std::to_string(i) + "," + std::to_string(j) + ")";
                erasure_map[key] = edge->state;
            }
        }

        for (int i = 0; i < nodeRows; i++)
        {
            for (int j = 0; j < nodeCols; j++)
            {
                auto edge = &vertical_edge_support[r * nodeRows * nodeCols + i * nodeCols + j];

                std::string key = "V(" + std::to_string(r) + "," + std::to_string(i) + "," + std::to_string(j) + ")";
                erasure_map[key] = edge->state;
            }
        }
    }

    return erasure_map;
}