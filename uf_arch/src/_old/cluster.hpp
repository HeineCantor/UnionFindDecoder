#ifndef _CLUSTER_HPP_
#define _CLUSTER_HPP_

#include "types.hpp"

class Cluster {
public:
    Cluster(int);

    auto get_id() const -> int { return id; }
    auto find() -> int { return root_node; }
    
private:
    static int id_counter;

    int id;
    int root_node;
};

#endif