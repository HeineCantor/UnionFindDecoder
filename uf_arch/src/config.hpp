#ifndef _CONFIG_HPP_
#define _CONFIG_HPP_

#include "types.hpp"

namespace config {
    // If true, the algorithm will remove cycles dynamically in the merge step, if a merge of a cluster with itself is detected.
    const bool DYNAMIC_CYCLE_PEEL = true;
}

#endif