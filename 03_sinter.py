import sinter
from typing import List
import stim
import matplotlib.pyplot as plt

if __name__ == "__main__":
    task = [
        sinter.Task(
            circuit=stim.Circuit.generated(
                "repetition_code:memory",
                rounds=d,
                distance=d,
                before_round_data_depolarization=noise
            ),
            json_metadata={'d':d, 'p':noise},
        )
        for d in [3, 5, 7, 9, 11, 13, 15, 17, 19, 21]
        for noise in [0.1, 0.2, 0.3, 0.4, 0.5]
    ]

    collected_stats: List[sinter.TaskStats] = sinter.collect(
        num_workers=14,
        tasks=task,
        max_shots=10**6,
        max_errors=500,
        decoders=['pymatching']
    )

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

    plt.show()