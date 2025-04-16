from qsurface.main import initialize, run
import math
from tqdm import tqdm

# Open syndrome file
# Each line is a syndrome, returns a list of syndromes
def open_syndrome_file(file_path):
    syndromes = []
    with open(file_path, 'r') as f:
        for line in f:
            syndromes.append(line.strip())
    return syndromes

# Open output file
# Each line is a prediction, returns a list of predictions
def open_output_file(file_path):
    predictions = []
    with open(file_path, 'r') as f:
        for line in f:
            predictions.append(line.strip())
    return predictions

CODE_DISTANCE = 5
CODE_SIZE = (CODE_DISTANCE, CODE_DISTANCE)
CODE_TYPE = "rotated"

ROUNDS = CODE_DISTANCE

NODE_ROWS = CODE_DISTANCE + 1
NODE_COLS = (CODE_DISTANCE - 1) // 2

if __name__ == "__main__":
    # Open syndrome file
    syndromes = open_syndrome_file('./uf_arch/val_files/syndrome.txt')

    # Open output file
    predictions = open_output_file('./uf_arch/val_files/output.txt')

    if len(syndromes) != len(predictions):
        print("The number of syndromes and predictions do not match.")
        exit(1)

    count_ez_errors = 0

    differenceIndexList = []

    # Convert syndromes to error_dict_for_qsurface format
    for i, syndrome in enumerate(tqdm(syndromes)):
        split_syndrome = syndrome.split()
        error_dict_for_qsurface = {}
        original_dict = {}
        for j in range(len(split_syndrome)):
            if split_syndrome[j] == '1':
                row = (j % (NODE_ROWS * NODE_COLS)) // NODE_COLS
                col = j % NODE_COLS
                round = j // (NODE_COLS * NODE_ROWS)

                original_dict[(row, col, round)] = True

                col += 0.5 + 2 * col * 0.5
                if row % 2 == 1:
                    col += 1

                row -= 0.5

                error_dict_for_qsurface[(col, row, round)] = True

        predictions_i = predictions[i]
        # Convert predictions to dict
        predictions_i = predictions_i.split('|')
        prediction_dict = {}
        for pred in predictions_i:
            if pred == '':
                continue
            prediction_dict[pred.split(':')[0]] = int(pred.split(':')[1])

        # print(original_dict)
        # print(error_dict_for_qsurface)
        code, decoder = initialize(CODE_SIZE, CODE_TYPE, "unionfind", enabled_errors=["pauli"], plotting=False, faulty_measurements=True, initial_states=(0,0))
        output = run(code, decoder, error_rates = {"p_bitflip": 0, "p_phaseflip": 0}, decode_initial=False, custom_error_dict=error_dict_for_qsurface)

        prematchings = output["prematchings"]
        # Only ez prematching
        prematchings_ez = {key: value for key, value in prematchings.items() if "ez" in str(key)}
        prematchings_ex = {key: value for key, value in prematchings.items() if "ex" in str(key)}

        for prematching in prematchings_ez:
            round = int(str(prematching).split('|')[-1])
            horizontal_coords = str(prematching).replace(f"|{round}", '')[4:-1]

            row = float(horizontal_coords.split(',')[1])
            col = float(horizontal_coords.split(',')[0])

            qsurf_prefix = str(prematching)[2]
            if qsurf_prefix == '-':
                custom_prefix = 'H'
            else:
                custom_prefix = 'V'
                round -= 1
                row += 0.5
                row = int(row)
                prevDataQubit = math.floor(col)
                if row % 2 == 0:
                    col = prevDataQubit / 2
                else:
                    col = (prevDataQubit - 1) / 2
            
            row = int(row)
            col = int(col)

            keyString = f"{custom_prefix}({round},{row},{col})"
            if keyString in prediction_dict:
                if prediction_dict[keyString] != prematchings_ez[prematching]:
                    count_ez_errors += 1
                    #print(f"Difference: {keyString} {prediction_dict[keyString]} {prematchings_ez[prematching]}")
                    if i not in differenceIndexList:
                        differenceIndexList.append(i)

    print(f"Detected {count_ez_errors} differences between algorithms.")
    print(f"Index list: {differenceIndexList}")
    print(f"Difference ratio: {count_ez_errors / len(syndromes) * 100:.2f}%")

