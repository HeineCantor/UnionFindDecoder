import sinter
from typing import List
import stim
import matplotlib.pyplot as plt
import numpy as np

from custom_decoders.unionfind.union_find_decoder import UnionFindDecoder

START_DISTANCE = 3
END_DISTANCE =   11

START_NOISE = 0.01
END_NOISE = 0.1

NOISE_STEP = 10

MAX_SHOTS = 10**5
MAX_ERRORS = MAX_SHOTS // 20
CORES = 14

DISTANCES = range(START_DISTANCE, END_DISTANCE+1, 2)
NOISES = np.linspace(START_NOISE, END_NOISE, NOISE_STEP).tolist()

CODE_TYPE = "surface_code:rotated_memory_z"
DECODER_TYPE = "union_find_decoder"

if __name__ == "__main__":
    task = [
        sinter.Task(
            circuit=stim.Circuit.generated(
                CODE_TYPE,
                rounds=d,
                distance=d,
                before_round_data_depolarization=noise
            ),
            json_metadata={'d':d, 'p':noise},
        )
        for d in DISTANCES
        for noise in NOISES
    ]

    collected_stats: List[sinter.TaskStats] = sinter.collect(
        num_workers=CORES,
        tasks=task,
        max_shots=MAX_SHOTS,
        max_errors=MAX_ERRORS,
        decoders=[DECODER_TYPE],
        custom_decoders={"union_find_decoder": UnionFindDecoder(CODE_TYPE)},
        print_progress=True
    )

    print("Distance|Noise:\t Time per decoder call")
    for stat in collected_stats:
        print(f"{stat.json_metadata['d']}|{stat.json_metadata['p']}:   \t {stat.seconds * 10**6 / stat.shots} us/dec || Accuracy: {1 - stat.errors / stat.shots}")

    fig, ax = plt.subplots(1, 1)
    sinter.plot_error_rate(
        ax=ax,
        stats=collected_stats,
        x_func=lambda stats: stats.json_metadata['p'],
        group_func=lambda stats: stats.json_metadata['d'],
    )
    ax.set_ylim(1e-4, 1e-0)
    ax.set_xlim(5e-2, 5e-1)
    ax.loglog()
    ax.set_title("Repetition Code Error Rates (Phenomenological Noise)")
    ax.set_xlabel("Phyical Error Rate")
    ax.set_ylabel("Logical Error Rate per Shot")
    ax.grid(which='major')
    ax.grid(which='minor')
    ax.legend()
    fig.set_dpi(120)  # Show it bigger

    plt.figure()

    # Plot time per decoder call vs distance
    for noise in NOISES:
        times = []
        for stat in collected_stats:
            if stat.json_metadata['p'] == noise:
                times.append(stat.seconds * 10**6 / stat.shots)
        plt.plot(DISTANCES, times, label=f"p={noise}", marker='o')

    plt.xlabel("Distance")
    plt.ylabel("Time per decoder call (us)")
    plt.title("Time per decoder call vs Distance")

    plt.legend()
    plt.grid()

    plt.show()