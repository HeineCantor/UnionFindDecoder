#ifndef _NODE_HPP_
#define _NODE_HPP_

#include <vector>
#include <set>
#include <algorithm>

#include "types.hpp"

class Node {
public:
    Node(int row, int col, Node* parent_id = nullptr) : row(row), col(col), parent(parent_id) {}

    Node* find(){
        if (this->parent == nullptr)
            return this;
    
        return this->parent->find();
    }

    bool cluster_union(Node* other) {
        Node* root1 = this->find();
        Node* root2 = other->find();

        if (root1 != root2) {
            root2->parent = root1;

            // Merge boundaries
            root1->boundary.insert(root2->boundary.begin(), root2->boundary.end());
            root2->boundary.clear();

            root1->on_border = root1->on_border || root2->on_border;
            root1->syndrome_count += root2->syndrome_count;
        }

        parity = root1->syndrome_count % 2 == 0;
        return parity;
    }

    int get_row() const { return row; }
    int get_col() const { return col; }

    void set_parent(Node* new_parent) { parent = new_parent; }
    void add_boundary_edge(EdgeCoords edge) { boundary.insert(edge); }
    void remove_boundary_edge(EdgeCoords edge) {
        this->find()->boundary.erase(edge);
    }

    bool on_border = false; // True if the node is on the code border
    bool is_syndrome = false; // True if the node is a syndrome
    bool parity = false; // Parity of the cluster
    int syndrome_count = 0; // Number of syndromes in the cluster
    std::set<EdgeCoords> boundary;

private:
    int row, col;                
    Node* parent = nullptr; 
};

#endif