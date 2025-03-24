# === Subject: Codes ===
SUBJECT_CODES = [ "unrotated", "rotated", "unrotated_xzzx", "rotated_xzzx" ]

# === Subject: Decoders ===
SUBJECT_DECODERS = [ "sparse_blossom", "union_find" ]

SUBJECTS = {
    "code" : SUBJECT_CODES,
    "decoder" : SUBJECT_DECODERS
}

SUBJECTS_QUICK = {
    "code" : [ "rotated" ],
    "decoder" : [ "sparse_blossom" ]
}

# === Repetitions ===

REPETITIONS = 2

# === Factors ===

#   === Constant Factors ===
CONSTANT_FACTORS = { 
    "p" : 0.05, 
    "shots" : 10000, 
    "rounds" : 100 
}

#   === Variable Factors ===
FACTORS = { 
    "distance" : range(3, 37 + 1, 2),
}

# === Response Variables ===

RESPONSE_VARIABLES = [ "error_rate", "runtime" ]