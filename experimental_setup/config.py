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

# === Factors ===

#   === Constant Factors ===
CONSTANT_FACTORS = {
    "shots" : 10**4,
}

#   === Variable Factors ===
FACTORS = { 
    "distance" : range(3, 31 + 1, 2),
    "rounds" : range(25, 100 + 1, 25)
}

# === Response Variables ===

RESPONSE_VARIABLES = [ "error_rate", "runtime [s]" ]