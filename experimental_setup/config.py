import numpy as np

# === Subject: Codes ===
REPETITION_CODE = "repetition"
UNROTATED_SURFACE_CODE = "unrotated"
ROTATED_SURFACE_CODE = "rotated"

# === Subject: Decoders ===
SPARSE_BLOSSOM_DECODER = "sparse_blossom"
UNION_FIND_DECODER = "union_find"
UF_ARCH_DECODER = "uf_arch"

# === Subject: Noise Models ===
SI1000_NOISE_MODEL = "si1000"
WILLOW_NOISE_MODEL = "willow"

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

CONSTANT_FACTORS_DSE = {
    "shots" : 10**5,
}

#   === Variable Factors ===
FACTORS = { 
    "distance" : range(3, 31 + 1, 2),
    "rounds" : range(25, 100 + 1, 25),
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

DSE_FACTORS_PEELING_ONLY = {
    # "distance" : range(3, 31 + 1, 2),
    # "base_error_rate" : np.linspace(0.001, 0.01, 10).tolist(),
    # "early_stopping_peeling" : range(3, 31+1, 2),
    "distance" : [9, 19, 29],
    "base_error_rate" : np.linspace(0.001, 0.01, 10).tolist(),
    "early_stopping_peeling" : range(3, 29 + 1, 2),
}

DSE_FACTORS = {
    "distance" : range(3, 31 + 1, 2),
    "base_error_rate" : np.linspace(0.001, 0.01, 10).tolist(),
    "early_stopping" : range(3, 31+1, 2),
    "early_stopping_peeling" : range(3, 31+1, 2),
}

# === Response Variables ===
ERROR_RATE_RESPONSE_VARIABLE = "error_rate"
RUNTIME_RESPONSE_VARIABLE = "runtime [s]"

# === Collections ===
SUBJECT_CODES = [ REPETITION_CODE, UNROTATED_SURFACE_CODE, ROTATED_SURFACE_CODE ]
SUBJECT_DECODERS = [ SPARSE_BLOSSOM_DECODER, UNION_FIND_DECODER ]
SUBJECT_NOISE_MODELS = [ SI1000_NOISE_MODEL, WILLOW_NOISE_MODEL ]

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

SUBJECTS_DSE = {
    "code" : [ ROTATED_SURFACE_CODE ],
    "decoder" : [ UF_ARCH_DECODER ],
    "noiseModel" : [ SI1000_NOISE_MODEL ]
}

RESPONSE_VARIABLES = [ ERROR_RATE_RESPONSE_VARIABLE, RUNTIME_RESPONSE_VARIABLE ]

# === Experimental Profiles ===
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
    "uf_arch_vs_sparse_blossom" : {
        "subjects" : {
            "code" : [ ROTATED_SURFACE_CODE ],
            "decoder" : [ SPARSE_BLOSSOM_DECODER, UF_ARCH_DECODER ],
            "noiseModel" : [ SI1000_NOISE_MODEL ]
        },
        "factors" : {
            "distance" : range(3, 27 + 1, 2),
            "base_error_rate" : np.linspace(0.001, 0.01, 10).tolist(),
        },
        "constant_factors" : {
            "shots" : 10**5
        },
        "repetitions" : 1,
        "response_variables" : RESPONSE_VARIABLES
    },
    "full" : {
        "subjects" : SUBJECTS,
        "factors" : FACTORS,
        "constant_factors" : CONSTANT_FACTORS,
        "repetitions" : REPETITIONS,
        "response_variables" : RESPONSE_VARIABLES
    },
    "dse_full" : {
        "subjects" : SUBJECTS_DSE,
        "factors" : DSE_FACTORS,
        "constant_factors" : CONSTANT_FACTORS_DSE,
        "repetitions" : REPETITIONS,
        "response_variables" : RESPONSE_VARIABLES,
        "rounds_as_distance" : True
    },
    "dse_peeling_only" : {
        "subjects" : SUBJECTS_DSE,
        "factors" : DSE_FACTORS_PEELING_ONLY,
        "constant_factors" : CONSTANT_FACTORS_DSE,
        "repetitions" : REPETITIONS,
        "response_variables" : RESPONSE_VARIABLES,
        "rounds_as_distance" : True
    },
        "dse_peeling_only_quick" : {
        "subjects" : SUBJECTS_DSE,
        "factors" : DSE_FACTORS_PEELING_ONLY,
        "constant_factors" : CONSTANT_FACTORS_DSE,
        "repetitions" : REPETITIONS,
        "response_variables" : RESPONSE_VARIABLES,
        "rounds_as_distance" : True
    }
}