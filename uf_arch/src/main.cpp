#include <iostream>
#include <vector>

#include "node.hpp"
#include "types.hpp"

std::vector<Node> initNodes(Syndrome2D& syndrome_2d) {
    std::vector<Node> nodes;
    
    for (std::size_t i = 0; i < syndrome_2d.size(); ++i) {
        for (std::size_t j = 0; j < syndrome_2d[i].size(); ++j) {
            Node node(i, j);
            
            node.is_syndrome = syndrome_2d[i][j] == 1;
            node.syndrome_count = syndrome_2d[i][j];

            if (j >= 1)
                node.add_boundary_edge(std::make_tuple(i, j - 1));
            if (j < syndrome_2d[i].size() - 1)
                node.add_boundary_edge(std::make_tuple(i, j));
            if (i > 0)
                node.add_boundary_edge(std::make_tuple(i - 1, j));
            if (i < syndrome_2d.size() - 1)
                node.add_boundary_edge(std::make_tuple(i + 1, j));

            nodes.push_back(node);
        }
    }

    return nodes;
}

int main() {
    // 2D Syndrome Mock
    Syndrome2D syndrome_2d = {
         {0, 0},
        {1, 0, 1},
         {0, 0},
        {0, 0, 0},
         {0, 0}
    };

    syndrome_2d = {
         {0, 0, 0, 0},
        {1, 0, 0, 0, 1},
         {0, 0, 0, 0},
        {0, 0, 0, 0, 0},
         {0, 0, 0, 0},
        {0, 0, 0, 0, 0},
         {0, 0, 0, 0},
        {0, 0, 1, 0, 1},
         {0, 0, 0, 0},
    };

    // 2D Edge Support Mock (everything is UNGROWN)
    EdgeSupport2D edge_support_2d = {
        {EdgeStatus::UNGROWN, EdgeStatus::UNGROWN, EdgeStatus::UNGROWN},
                {EdgeStatus::UNGROWN, EdgeStatus::UNGROWN},
        {EdgeStatus::UNGROWN, EdgeStatus::UNGROWN, EdgeStatus::UNGROWN},
                {EdgeStatus::UNGROWN, EdgeStatus::UNGROWN},
        {EdgeStatus::UNGROWN, EdgeStatus::UNGROWN, EdgeStatus::UNGROWN}
    };

    edge_support_2d = {
        {EdgeStatus::UNGROWN, EdgeStatus::UNGROWN, EdgeStatus::UNGROWN, EdgeStatus::UNGROWN, EdgeStatus::UNGROWN},
                {EdgeStatus::UNGROWN, EdgeStatus::UNGROWN, EdgeStatus::UNGROWN, EdgeStatus::UNGROWN},
        {EdgeStatus::UNGROWN, EdgeStatus::UNGROWN, EdgeStatus::UNGROWN, EdgeStatus::UNGROWN, EdgeStatus::UNGROWN},
                {EdgeStatus::UNGROWN, EdgeStatus::UNGROWN, EdgeStatus::UNGROWN, EdgeStatus::UNGROWN},
        {EdgeStatus::UNGROWN, EdgeStatus::UNGROWN, EdgeStatus::UNGROWN, EdgeStatus::UNGROWN, EdgeStatus::UNGROWN},
                {EdgeStatus::UNGROWN, EdgeStatus::UNGROWN, EdgeStatus::UNGROWN, EdgeStatus::UNGROWN},
        {EdgeStatus::UNGROWN, EdgeStatus::UNGROWN, EdgeStatus::UNGROWN, EdgeStatus::UNGROWN, EdgeStatus::UNGROWN},
                {EdgeStatus::UNGROWN, EdgeStatus::UNGROWN, EdgeStatus::UNGROWN, EdgeStatus::UNGROWN},
        {EdgeStatus::UNGROWN, EdgeStatus::UNGROWN, EdgeStatus::UNGROWN, EdgeStatus::UNGROWN, EdgeStatus::UNGROWN}
    };

    // Initialize nodes from syndrome
    std::vector<Node> nodes = initNodes(syndrome_2d);

    // Initialize cluster roots
    std::set<Node*> cluster_roots;
    for (auto& node : nodes)
        if (node.is_syndrome)
            cluster_roots.insert(node.find());

    // Initialize fusion edges (edges grown after a UF loop)
    std::vector<EdgeCoords> fusionEdges;

    while (cluster_roots.size() > 0)
    {
        auto size = cluster_roots.size();
        for (const auto& root : cluster_roots) {
            auto row = root->get_row();
            auto col = root->get_col();

            if (row % 2 == 0) // Skip even rows (only Z Syndromes)
                continue; 

            for (auto& boundary : root->boundary)
            {
                auto boundaryRow = std::get<0>(boundary);
                auto boundaryCol = std::get<1>(boundary);

                if (edge_support_2d[boundaryRow][boundaryCol] != EdgeStatus::GROWN)
                {
                    edge_support_2d[boundaryRow][boundaryCol] = static_cast<EdgeStatus>(static_cast<int>(edge_support_2d[boundaryRow][boundaryCol]) + 1);
                    
                    if (edge_support_2d[boundaryRow][boundaryCol] == EdgeStatus::GROWN)
                        fusionEdges.push_back(std::make_tuple(boundaryRow, boundaryCol));
                }
            }
        }

        for (const auto& edge : fusionEdges) {
            int row = std::get<0>(edge);
            int col = std::get<1>(edge);

            // Find the nodes connected by this edge
            Node* node1 = nullptr;
            Node* node2 = nullptr;

            for (auto& node : nodes) {
                if (row % 2 == 1 && node.get_row() == row && node.get_col() == col) {
                    node1 = &node;
                }
                else if (row % 2 == 1 && node.get_row() == row && node.get_col() == col + 1) {
                    node2 = &node;
                }
                else if (row % 2 == 0 && node.get_row() == row - 1 && node.get_col() == col) {
                    node1 = &node;
                }
                else if (row % 2 == 0 && node.get_row() == row + 1 && node.get_col() == col) {
                    node2 = &node;
                }
            }


            if (node1 && node2) {
                // Check if the nodes belong to different clusters
                // If they do, merge the clusters
                if (node1->find() != node2->find()) {
                    cluster_roots.erase(node2->find());
                    if (node1->cluster_union(node2)) 
                        cluster_roots.erase(node1->find());
                    else if (!node1->find()->on_border)
                        cluster_roots.insert(node1->find());
                    node1->remove_boundary_edge(edge);
                } 
                else {
                    // If they belong to the same cluster, just remove the edge (without creating loops)
                    node1->remove_boundary_edge(edge);
                }
            }
            else if (node1 || node2) {
                // If one of the nodes is not found, it means the edge is on the code border
                if (node1) {
                    node1->find()->on_border = true;
                    cluster_roots.erase(node1->find());
                }
                else if (node2) {
                    node2->find()->on_border = true;
                    cluster_roots.erase(node2->find());
                }
                
                std::cout << "Code Border: " << row << "|" << col << std::endl;
            }
            else {
                std::cerr << "Error: Edge not found in any node." << std::endl;
            }
        }

        fusionEdges.clear();
    }

    // Print the edge support status
    for (std::size_t i = 0; i < edge_support_2d.size(); ++i) {
        if (i%2 == 1)
            std::cout << " ";
        for (std::size_t j = 0; j < edge_support_2d[i].size(); ++j) {
            std::cout << static_cast<int>(edge_support_2d[i][j]) << " ";
        }
        std::cout << std::endl;
    }

    // Print the nodes and their syndromes
    std::cout << "Clusters:" << std::endl;
    for (auto& node : nodes) {
        auto root = node.find();

        if (!root->syndrome_count)
            continue;

        std::cout << "Node ID: (" << node.get_row() << ", " << node.get_col() << ") | Root ID: (" << root->get_row() << ", " << root->get_col() << ")";
        std::cout << " | Syndrome Count: " << root->syndrome_count;
        std::cout << " | On Border: " << (root->on_border ? "Yes" : "No");
        // std::cout << " | Boundary Edges: ";
        // for (const auto& edge : root->boundary) {
        //     std::cout << "(" << std::get<0>(edge) << ", " << std::get<1>(edge) << ") ";
        // }
        std::cout << std::endl;
    }

    return 0;
}