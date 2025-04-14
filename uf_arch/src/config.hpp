#ifndef _CONFIG_HPP_
#define _CONFIG_HPP_

#include <string>

namespace config {
    enum CodeType {
        UNROTATED,
        ROTATED,
        REPETITION
    };

    // Code distance
    const int CODE_DISTANCE = 5;

    // Rounds
    const int ROUNDS = CODE_DISTANCE;

    // Code type
    const CodeType CODE_TYPE = ROTATED;

    const int NODES_ROWS = CODE_TYPE == UNROTATED ? CODE_DISTANCE
        : CODE_TYPE == ROTATED ? CODE_DISTANCE + 1
        : CODE_TYPE == REPETITION ? 1
        : 0;

    const int NODES_COLS = CODE_TYPE == UNROTATED ? CODE_DISTANCE - 1
        : CODE_TYPE == ROTATED ? (CODE_DISTANCE - 1) / 2
        : CODE_TYPE == REPETITION ? CODE_DISTANCE - 1
        : 0;

    const int EDGES_ROWS = CODE_TYPE == UNROTATED ? CODE_DISTANCE * 2 - 1
        : CODE_TYPE == ROTATED ? CODE_DISTANCE
        : CODE_TYPE == REPETITION ? 1
        : 0;

    const int EDGES_COLS = CODE_TYPE == UNROTATED ? CODE_DISTANCE
        : CODE_TYPE == ROTATED ? CODE_DISTANCE
        : CODE_TYPE == REPETITION ? CODE_DISTANCE
        : 0;
}

#endif