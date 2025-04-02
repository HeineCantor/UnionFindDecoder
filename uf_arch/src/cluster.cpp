#include "cluster.hpp"

int Cluster::id_counter = 0;

Cluster::Cluster(int root_node) : root_node(root_node) {
    id = Cluster::id_counter++;
}