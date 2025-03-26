import numpy as np

# === Subject: Codes ===
SUBJECT_CODES = [ "repetition", "unrotated", "rotated" ]

# === Subject: Decoders ===
SUBJECT_DECODERS = [ "sparse_blossom", "union_find" ]

# === Subject: Noise Models ===
SUBJECT_NOISE_MODELS = [ "si1000_004", "willow" ]

SUBJECTS = {
    "code" : SUBJECT_CODES,
    "decoder" : SUBJECT_DECODERS,
    "noiseModel" : SUBJECT_NOISE_MODELS
}

SUBJECTS_QUICK = {
    "code" : [ "rotated" ],
    "decoder" : [ "sparse_blossom" ],
    "noiseModel" : [ "willow" ]
}

# === Repetitions ===

REPETITIONS = 1

REPETITIONS_PRELIM_VARIANCE = 100

#   === Constant Factors ===

CONSTANT_FACTORS = {
    "shots" : 10**4,
}

CONSTANT_FACTORS_PRELIM_DISTANCE = {
    "shots" : 10**4,
    "rounds" : 100
}

CONSTANT_FACTORS_PRELIM_SHOTS = {
    "rounds" : 100,
    "distance" : 23
}

CONSTANT_FACTORS_PRELIM_ROUNDS = {
    "shots" : 10**4,
    "distance" : 23
}

CONSTANT_FACTORS_PRELIM_VARIANCE = {
    "shots" : 10**3,
    "rounds" : 100,
    "distance" : 23
}

#   === Variable Factors ===

FACTORS = { 
    "distance" : range(3, 31 + 1, 2),
    "rounds" : range(25, 100 + 1, 25)
}

FACTORS_PRELIM_DISTANCE = {
    "distance" : range(3, 31 + 1, 2),
}

FACTORS_PRELIM_SHOTS = {
    "shots" : np.linspace(10**3, 10**4, 10, dtype=int).tolist()
}

FACTORS_PRELIM_ROUNDS = {
    "rounds" : np.linspace(25, 100, 10, dtype=int).tolist()
}

FACTORS_PRELIM_VARIANCE = {}

# === Response Variables ===

RESPONSE_VARIABLES = [ "error_rate", "runtime [s]" ]

profiles = {
    "quick" : {
        "subjects" : SUBJECTS_QUICK,
        "factors" : FACTORS,
        "constant_factors" : CONSTANT_FACTORS,
        "repetitions" : REPETITIONS,
        "response_variables" : RESPONSE_VARIABLES
    },
    "preliminary_distance" : {
        "subjects" : SUBJECTS,
        "factors" : FACTORS_PRELIM_DISTANCE,
        "constant_factors" : CONSTANT_FACTORS_PRELIM_DISTANCE,
        "repetitions" : REPETITIONS,
        "response_variables" : RESPONSE_VARIABLES
    },
    "preliminary_shots" : {
        "subjects" : SUBJECTS,
        "factors" : FACTORS_PRELIM_SHOTS,
        "constant_factors" : CONSTANT_FACTORS_PRELIM_SHOTS,
        "repetitions" : REPETITIONS,
        "response_variables" : RESPONSE_VARIABLES
    },
    "preliminary_rounds" : {
        "subjects" : SUBJECTS,
        "factors" : FACTORS_PRELIM_ROUNDS,
        "constant_factors" : CONSTANT_FACTORS_PRELIM_DISTANCE,
        "repetitions" : REPETITIONS,
        "response_variables" : RESPONSE_VARIABLES
    },
    "preliminary_variance" : {
        "subjects" : SUBJECTS,
        "factors" : FACTORS_PRELIM_VARIANCE,
        "constant_factors" : CONSTANT_FACTORS_PRELIM_VARIANCE,
        "repetitions" : REPETITIONS_PRELIM_VARIANCE,
        "response_variables" : RESPONSE_VARIABLES
    },
    "full" : {
        "subjects" : SUBJECTS,
        "factors" : FACTORS,
        "constant_factors" : CONSTANT_FACTORS,
        "repetitions" : REPETITIONS,
        "response_variables" : RESPONSE_VARIABLES
    }
}