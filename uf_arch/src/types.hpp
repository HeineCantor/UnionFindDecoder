#ifndef _TYPES_HPP_
#define _TYPES_HPP_

#include <vector>
#include <tuple>

enum class EdgeStatus {
    PEELED = -1,
    UNGROWN = 0,
    HALF_GROWN = 1,
    GROWN = 2
};

typedef std::vector<std::vector<int>> Syndrome2D;
typedef std::vector<std::vector<EdgeStatus>> EdgeSupport2D;
typedef std::tuple<int, int> EdgeCoords;

#endif