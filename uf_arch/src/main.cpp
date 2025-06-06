#include <iostream>
#include <vector>
#include <set>
#include <chrono>
#include <fstream>
#include <sstream>

#include "union_find.hpp"

#include "types.hpp"
#include "config.hpp"
#include "utils.hpp"

#define DISTANCE 27
#define ROUNDS DISTANCE+1
#define CODE_TYPE CodeType::ROTATED

#define VALIDATION_SHOTS 100000

#define SYNDROME_FILE "val_files/syndrome.txt"
#define OUTPUT_FILE "val_files/output.txt"

void generate_validation_files()
{
    UnionFindDecoder ufDecoder(DISTANCE, ROUNDS, CODE_TYPE);
    auto totalDuration = 0;

    srand(time(NULL)); // Seed for random number generation

    // Create output directory if it doesn't exist
    std::string command = "mkdir -p val_files";
    if (system(command.c_str()) != 0)
    {
        std::cerr << "Error creating directory" << std::endl;
        return;
    }

    // Delete output files
    std::remove(SYNDROME_FILE);
    std::remove(OUTPUT_FILE);

    auto nodeCols = getNodeColsByCodeAndDistance(CODE_TYPE, DISTANCE);
    auto nodeRows = getNodeRowsByCodeAndDistance(CODE_TYPE, DISTANCE);

    for (int i = 0; i < VALIDATION_SHOTS; i++)
    {
        auto syndromes = generate_random_syndrome(nodeCols * nodeRows * ROUNDS, 0.01);
        ufDecoder = UnionFindDecoder(DISTANCE, ROUNDS, CODE_TYPE);

        auto start = std::chrono::high_resolution_clock::now();    

        ufDecoder.initCluster(syndromes);
        ufDecoder.grow();

        auto end = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start).count();

        totalDuration += duration;

        // Append generated syndrome to syndrome file
        std::ofstream syndromeFile(SYNDROME_FILE, std::ios::app);
        if (syndromeFile.is_open())
        {
            for (const auto& s : syndromes)
            {
                syndromeFile << s << " ";
            }
            syndromeFile << std::endl;
            syndromeFile.close();
        }
        else
        {
            std::cerr << "Unable to open file" << std::endl;
        }

        // Append output to output file
        std::ofstream outputFile(OUTPUT_FILE, std::ios::app);
        if (outputFile.is_open())
        {
            auto erasureMap = get_erasure_map(ufDecoder.edge_support, ufDecoder.vertical_edge_support, ROUNDS, CODE_TYPE, DISTANCE);
            for (const auto& entry : erasureMap)
            {
                outputFile << entry.first << ": " << entry.second << "|";
            }
            outputFile << std::endl;
        }
        else
        {
            std::cerr << "Unable to open file" << std::endl;
        }
    }

    totalDuration /= VALIDATION_SHOTS;
    std::cout << "Average time taken: " << totalDuration << " microseconds" << std::endl;
}

void decode_specific(int index)
{
    // decode a syndrome from syndrome file
    std::ifstream syndromeFile(SYNDROME_FILE);
    if (!syndromeFile.is_open())
    {
        std::cerr << "Unable to open syndrome file" << std::endl;
        return;
    }

    std::string line;
    int lineIndex = 0;

    while (std::getline(syndromeFile, line))
    {
        if (lineIndex == index)
        {
            std::istringstream iss(line);
            std::vector<bool> syndromes;
            bool s;
            while (iss >> s)
            {
                syndromes.push_back(s);
            }

            UnionFindDecoder ufDecoder(DISTANCE, ROUNDS, CODE_TYPE);
            ufDecoder.initCluster(syndromes);
            ufDecoder.grow();

            auto erasureMap = get_erasure_map(ufDecoder.edge_support, ufDecoder.vertical_edge_support, ROUNDS, CODE_TYPE, DISTANCE);
            for (const auto& entry : erasureMap)
            {
                std::cout << entry.first << ": " << entry.second << "|";
            }
            std::cout << std::endl;

            break;
        }
        lineIndex++;
    }
}

void randomSyndromeDecoding(int initParallelParam = 1, int growParallelParam = 1, int earlyStoppingParam = -1)
{
    auto nodeCols = getNodeColsByCodeAndDistance(CODE_TYPE, DISTANCE);
    auto nodeRows = getNodeRowsByCodeAndDistance(CODE_TYPE, DISTANCE);

    // Decode a random syndrome
    std::vector<bool> syndromes = generate_random_syndrome(nodeCols * nodeRows * ROUNDS, 0.1);

    // syndromes = {
    //     0, 0, 0, 0,
    //     0, 0, 0, 0,
    //     0, 0, 0, 1,
    //     0, 0, 1, 0,
    // };

    syndromes =  { 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0};

    std::cout << "Syndrome: ";
    for (const auto& s : syndromes)
        std::cout << s << " ";
    std::cout << std::endl;

    UnionFindDecoder ufDecoder = UnionFindDecoder(DISTANCE, ROUNDS, CODE_TYPE, initParallelParam, growParallelParam, earlyStoppingParam);

    ufDecoder.decode(syndromes);

    auto horizontalCorrections = ufDecoder.get_horizontal_corrections();
    std::cout << "Horizontal corrections: ";
    for (const auto& c : horizontalCorrections)
        std::cout << "(" << std::get<0>(c) << ", " << std::get<1>(c) << ", " << std::get<2>(c) << ") ";
    std::cout << std::endl;

    // auto erasureMap = get_erasure_map(ufDecoder.edge_support, ufDecoder.vertical_edge_support, ROUNDS, CODE_TYPE, DISTANCE);
    
    // for (const auto& entry : erasureMap)
    //     if (entry.second == -2)
    //         std::cout << entry.first << ": " << entry.second << std::endl;
    
    // std::cout << std::endl;

    auto stats = ufDecoder.get_stats();
    std::cout << "Grow/merge iterations: " << stats.num_grow_merge_iters << std::endl;
    
    std::cout << "Average boundaries per iteration: ";
    for (const auto& b : stats.boundaries_per_iter)
        std::cout << b << " ";
    std::cout << std::endl;

    std::cout << "Average merges per iteration: ";
    for (const auto& m : stats.merges_per_iter)
        std::cout << m << " ";
    std::cout << std::endl;

    std::cout << "Average odd clusters per iteration: ";
    for (const auto& o : stats.odd_clusters_per_iter)
        std::cout << o << " ";
    std::cout << std::endl;
}

int main()
{
    // generate_validation_files();    
    // decode_specific(16484);
    randomSyndromeDecoding(4, 4, -1);

    return 0;
}