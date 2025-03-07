import stim
import matplotlib.pyplot as plt
import utils
import numpy as np

from tqdm import tqdm

NUM_SHOTS = 10**6

DISTANCE_LIST = range(3, 9+1, 2)
DEP_NOISE_LIST = np.arange(0.1, 0.6, 0.1).tolist()

for distance in tqdm(DISTANCE_LIST):
    xPhysicalError = []
    yLogicalError = []

    for noise in tqdm(DEP_NOISE_LIST):
        repetitionCode = stim.Circuit.generated(
            "repetition_code:memory",
            rounds=distance,
            distance=distance,
            before_round_data_depolarization=noise
        )

        xPhysicalError.append(noise)
        yLogicalError.append(utils.countLogicalErrors(repetitionCode, NUM_SHOTS) / NUM_SHOTS)
    
    plt.plot(xPhysicalError, yLogicalError, label=f"Distance {distance}")

plt.loglog()
plt.xlabel("Physical error rate")
plt.ylabel("Logical error rate")
plt.legend()
plt.grid()
plt.show()
