#include <iostream>
#include <vector>
#include <chrono>

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

Syndrome2D generateRandomZSyndrome(int dx, int dy, float p = 0.1) {
    Syndrome2D syndrome;
    srand((unsigned)time(0)); 

    std::vector<int> row;
    for (int i = 0; i < 2*dx-1; ++i) {
        for (int j = 0; j < dy - (1-i%2); ++j) {
            if (i % 2 == 0) {
                row.push_back(0);
            } else {
                if ((rand() % 101) < p*100) {
                    row.push_back(1);
                } else {
                    row.push_back(0);
                }
            }

        }
        syndrome.push_back(row);
        row.clear();
    }

    return syndrome;
}

EdgeSupport2D generateSupport(int dx, int dy) {
    EdgeSupport2D edge_support;

    for (int i = 0; i < 2*dx-1; ++i) {
        std::vector<EdgeStatus> row;
        for (int j = 0; j < dy - i%2; ++j) {
            row.push_back(EdgeStatus::UNGROWN);
        }
        edge_support.push_back(row);
    }

    return edge_support;
}

const int TEST_DISTANCE = 25;

int main() {
    using std::chrono::high_resolution_clock;
    using std::chrono::duration_cast;
    using std::chrono::duration;
    using std::chrono::microseconds;

    // 2D Syndrome
    Syndrome2D syndrome_2d = generateRandomZSyndrome(TEST_DISTANCE, TEST_DISTANCE, 0.1);

    // 2D Edge Support
    EdgeSupport2D edge_support_2d = generateSupport(TEST_DISTANCE, TEST_DISTANCE);

    // Initialize nodes from syndrome
    std::vector<Node> nodes = initNodes(syndrome_2d);

    // Print the syndrome
    std::cout << "Syndrome:" << std::endl;
    for (std::size_t i = 0; i < syndrome_2d.size(); ++i) {
        if (i%2 == 0)
            std::cout << " ";
        for (std::size_t j = 0; j < syndrome_2d[i].size(); ++j) {
            std::cout << syndrome_2d[i][j] << " ";
        }
        std::cout << std::endl;
    }
    std::cout << std::endl;

    // Initialize cluster roots
    std::set<Node*> cluster_roots;
    for (auto& node : nodes)
        if (node.is_syndrome)
            cluster_roots.insert(node.find());

    // Initialize fusion edges (edges grown after a UF loop)
    std::vector<EdgeCoords> fusionEdges;

    auto start = high_resolution_clock::now();

    auto t1 = high_resolution_clock::now();
    auto t2 = high_resolution_clock::now();
    auto t3 = high_resolution_clock::now();
    while (cluster_roots.size() > 0)
    {
        auto size = cluster_roots.size();

        t1 = high_resolution_clock::now();
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

        t2 = high_resolution_clock::now();
        for (const auto& edge : fusionEdges) {
            int row = std::get<0>(edge);
            int col = std::get<1>(edge);

            // Find the nodes connected by this edge
            Node* node1 = nullptr;
            Node* node2 = nullptr;

            // TODO: direct access instead of iterating
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
                    edge_support_2d[row][col] = EdgeStatus::PEELED;
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
            }
            else {
                std::cerr << "Error: Edge not found in any node." << std::endl;
            }
        }

        t3 = high_resolution_clock::now();

        auto t2_1_duration = duration_cast<microseconds>(t2 - t1).count();
        auto t3_2_duration = duration_cast<microseconds>(t3 - t2).count();

        std::cout << "UF loop duration: " << t2_1_duration << " microseconds" << std::endl;
        std::cout << "UF loop duration (fusion edges): " << t3_2_duration << " microseconds" << std::endl;

        fusionEdges.clear();
    }
    auto end = high_resolution_clock::now();
    auto us_duration = duration_cast<microseconds>(end - start).count();

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
    // std::cout << "Clusters:" << std::endl;
    // for (auto& node : nodes) {
    //     auto root = node.find();

    //     if (!root->syndrome_count)
    //         continue;

    //     std::cout << "Node ID: (" << node.get_row() << ", " << node.get_col() << ") | Root ID: (" << root->get_row() << ", " << root->get_col() << ")";
    //     std::cout << " | Syndrome Count: " << root->syndrome_count;
    //     std::cout << " | On Border: " << (root->on_border ? "Yes" : "No");
    //     // std::cout << " | Boundary Edges: ";
    //     // for (const auto& edge : root->boundary) {
    //     //     std::cout << "(" << std::get<0>(edge) << ", " << std::get<1>(edge) << ") ";
    //     // }
    //     std::cout << std::endl;
    // }

    std::cout << "UF loop duration: " << us_duration << " microseconds" << std::endl;
    return 0;
}