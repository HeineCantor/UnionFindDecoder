import numpy as np

# === Subject: Codes ===
REPETITION_CODE = "repetition"
UNROTATED_SURFACE_CODE = "unrotated"
ROTATED_SURFACE_CODE = "rotated"

SUBJECT_CODES = [ REPETITION_CODE, UNROTATED_SURFACE_CODE, ROTATED_SURFACE_CODE ]

# === Subject: Decoders ===
SPARSE_BLOSSOM_DECODER = "sparse_blossom"
UNION_FIND_DECODER = "union_find"

SUBJECT_DECODERS = [ SPARSE_BLOSSOM_DECODER, UNION_FIND_DECODER ]

# === Subject: Noise Models ===
SI1000_004_NOISE_MODEL = "si1000_004"
WILLOW_NOISE_MODEL = "willow"

SUBJECT_NOISE_MODELS = [ SI1000_004_NOISE_MODEL, WILLOW_NOISE_MODEL ]

SUBJECTS = {
    "code" : SUBJECT_CODES,
    "decoder" : SUBJECT_DECODERS,
    "noiseModel" : SUBJECT_NOISE_MODELS
}

SUBJECTS_MOCK = {
    "code" : [ ROTATED_SURFACE_CODE ],
    "decoder" : [ SPARSE_BLOSSOM_DECODER ],
    "noiseModel" : [ WILLOW_NOISE_MODEL ]
}

SUBJECTS_QUICK = {
    "code" : [ REPETITION_CODE, ROTATED_SURFACE_CODE ],
    "decoder" : [ SPARSE_BLOSSOM_DECODER ],
    "noiseModel" : SUBJECT_NOISE_MODELS
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
ERROR_RATE_RESPONSE_VARIABLE = "error_rate"
RUNTIME_RESPONSE_VARIABLE = "runtime [s]"

RESPONSE_VARIABLES = [ ERROR_RATE_RESPONSE_VARIABLE, RUNTIME_RESPONSE_VARIABLE ]

profiles = {
    "mock": {
        "subjects" : SUBJECTS_MOCK,
        "factors" : FACTORS,
        "constant_factors" : CONSTANT_FACTORS,
        "repetitions" : 1,
        "response_variables" : RESPONSE_VARIABLES
    },
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