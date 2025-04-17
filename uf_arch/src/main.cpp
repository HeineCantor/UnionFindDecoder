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

#define VALIDATION_SHOTS 100000

#define SYNDROME_FILE "val_files/syndrome.txt"
#define OUTPUT_FILE "val_files/output.txt"

void generate_validation_files()
{
    UnionFindDecoder ufDecoder;
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

    for (int i = 0; i < VALIDATION_SHOTS; i++)
    {
        auto syndromes = generate_random_syndrome(config::NODES_COLS * config::NODES_ROWS * config::ROUNDS, 0.01);
        ufDecoder = UnionFindDecoder();

        auto start = std::chrono::high_resolution_clock::now();    

        ufDecoder.init_clusters(syndromes);
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
            auto erasureMap = get_erasure_map(ufDecoder.get_edge_support(), ufDecoder.get_vertical_edge_support());
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

            UnionFindDecoder ufDecoder;
            ufDecoder.init_clusters(syndromes);
            ufDecoder.grow();

            auto erasureMap = get_erasure_map(ufDecoder.get_edge_support(), ufDecoder.get_vertical_edge_support());
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

int main()
{
    generate_validation_files();    
    // decode_specific(16484);

    return 0;
}