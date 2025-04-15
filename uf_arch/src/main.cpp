#include <iostream>
#include <vector>
#include <set>
#include <chrono>

#include "union_find.hpp"

#include "types.hpp"
#include "config.hpp"
#include "utils.hpp"

int main()
{
    // Testing
    auto syndromes = generate_random_syndrome(config::NODES_COLS * config::NODES_ROWS * config::ROUNDS, 0.01);

    std::cout << "Syndromes: ";
    for (auto s : syndromes)
        std::cout << (s ? "1" : "0");
    std::cout << std::endl;

    auto start = std::chrono::high_resolution_clock::now();

    UnionFindDecoder ufDecoder = UnionFindDecoder();

    ufDecoder.init_clusters(syndromes);
    ufDecoder.grow();

    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start).count();
    
    std::cout << "Final edge support matrix: " << std::endl;
    print_edge_support_matrix(ufDecoder.get_edge_support());
    std::cout << "Final vertical edge support matrix: " << std::endl;
    print_vertical_edge_support_matrix(ufDecoder.get_vertical_edge_support());

    std::cout << "Time taken: " << duration << " microseconds" << std::endl;

    return 0;
}