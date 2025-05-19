from stim import Circuit
import pymatching
import numpy as np

from tqdm import tqdm

from qsurface.main import initialize, run

def saveSVG(stimCircuit : Circuit, diagramType : str, name : str):
    if diagramType == "timeslice-svg":
        svg = str(stimCircuit.diagram(diagramType, tick=range(0, 18)))
    else:
        svg = str(stimCircuit.diagram(diagramType))
    with open(f"{name}.svg", "w") as f:
        f.write(svg)

def saveGLTF(stimCircuit : Circuit, diagramType : str, name : str):
    gltf = stimCircuit.diagram(diagramType)
    with open(f"{name}.gltf", "w") as f:
        f.write(str(gltf))

def countLogicalErrors_uf_repetition(circuit: Circuit, shots: int) -> int:
    sampler = circuit.compile_detector_sampler()
    detectionEvents, observableFlips = sampler.sample(shots=shots, separate_observables=True)

    detectorErrorModel = circuit.detector_error_model(decompose_errors=True)
    detCoords = detectorErrorModel.get_detector_coordinates()

    codeDistance = int(list(detCoords.values())[-1][0]) // 2

    convCoords = {}
    for i in range(len(detCoords)):
        convCoords[i] = (detCoords[i][0] / 2 - 0.5, detCoords[i][1] / 2 - 0.5, detCoords[i][2])

def countLogicalErrors_uf_rotated(circuit: Circuit, rounds: int, shots: int) -> int:
    sampler = circuit.compile_detector_sampler()
    detectionEvents, observableFlips = sampler.sample(shots=shots, separate_observables=True)

    detectorErrorModel = circuit.detector_error_model(decompose_errors=True)
    detCoords = detectorErrorModel.get_detector_coordinates()

    codeDistance = int(list(detCoords.values())[-1][0]) // 2

    convCoords = {}
    for i in range(len(detCoords)):
        convCoords[i] = (detCoords[i][0] / 2 - 0.5, detCoords[i][1] / 2 - 0.5, detCoords[i][2])

    numErrors = 0

    print("Initializing decoder")
    for shot in tqdm(range(shots)):
        code, decoder = initialize((codeDistance, codeDistance, rounds), "rotated", "unionfind", enabled_errors=["pauli"], faulty_measurements=True, initial_states=(0,0)
                                   , plotting=False)
        
        triggeredDetectorCoords = []
        for detIndex in range(len(detectionEvents[shot])):
            if detectionEvents[shot][detIndex]:
                triggeredDetectorCoords.append(detCoords[detIndex])

        error_dict_for_qsurface = {}

        for i, err in enumerate(detectionEvents[shot]):
            if err == 1:
                error_dict_for_qsurface[convCoords[i]] = err

        output = run(code, decoder, error_rates = {"p_bitflip": 0.1, "p_phaseflip": 0.1}, decode_initial=False, custom_error_dict=error_dict_for_qsurface)
        matchings = output["matchings"]
        originalMatchings = matchings

        matchings = [str(m[0]).removeprefix("ex-").removeprefix("ex|").split('|')[0] for m in matchings if "ex" in str(m[0])]
        matchings = [(float(m.split(',')[0][1:]), float(m.split(',')[1][:-1])) for m in matchings]
        matchings = [(int((m[0] + 0.5) * 2), int((m[1] + 0.5) * 2)) for m in matchings]

        tmpParity = 0

        for m in matchings:
            if m[1] == 1:
                tmpParity ^= 1

        if tmpParity != observableFlips[shot]:
            numErrors += 1

        print(numErrors)
    return numErrors

def countLogicalErrors_uf(circuit: Circuit, shots: int) -> int:
    sampler = circuit.compile_detector_sampler()
    detectionEvents, observableFlips = sampler.sample(shots=shots, separate_observables=True)

    detectorErrorModel = circuit.detector_error_model(decompose_errors=True)
    detCoords = detectorErrorModel.get_detector_coordinates()

    codeDistance = int(list(detCoords.values())[-1][-1])

    convCoords = {}
    for i in range(len(detCoords)):
        convCoords[i] = (detCoords[i][0] / 2 + 0.5, detCoords[i][1] / 2, detCoords[i][2])

    numErrors = 0

    for shot in (pbar := tqdm(range(shots))):
        code, decoder = initialize((codeDistance, codeDistance), "planar", "unionfind", enabled_errors=["pauli"], faulty_measurements=True, initial_states=(0,0), plotting=False)

        triggeredDetectorCoords = []
        for detIndex in range(len(detectionEvents[shot])):
            if detectionEvents[shot][detIndex]:
                triggeredDetectorCoords.append(detCoords[detIndex])

        error_dict_for_qsurface = {}

        for i, err in enumerate(detectionEvents[shot]):
            if err == 1:
                error_dict_for_qsurface[convCoords[i]] = err

        output = run(code, decoder, error_rates = {"p_bitflip": 0.1, "p_phaseflip": 0.1}, decode_initial=False, custom_error_dict=error_dict_for_qsurface)
        matchings = output["matchings"]
        originalMatchings = matchings

        matchings = [str(m[0]).removeprefix("ez-").removeprefix("ez|").split('|')[0] for m in matchings if "ez" in str(m[0])]
        matchings = [(float(m.split(',')[0][1:]), float(m.split(',')[1][:-1])) for m in matchings]
        matchings = [(int((m[0] - 0.5) * 2), int(m[1] * 2)) for m in matchings]

        tmpParity = 0

        for m in matchings:
            if m[1] == 0:
                tmpParity ^= 1

        if tmpParity != observableFlips[shot]:
            numErrors += 1

    return numErrors

def countLogicalErrors(circuit: Circuit, shots: int) -> int:
    sampler = circuit.compile_detector_sampler()
    detectionEvents, observableFlips = sampler.sample(shots=shots, separate_observables=True)

    detectorErrorModel = circuit.detector_error_model(decompose_errors=True)
    matcher = pymatching.Matching.from_detector_error_model(detectorErrorModel)
    detCoords = detectorErrorModel.get_detector_coordinates()

    triggeredDetectorCoords = []
    for shot in range(shots):
        for detIndex in range(len(detectionEvents[shot])):
            if detectionEvents[shot][detIndex]:
                triggeredDetectorCoords.append(detCoords[detIndex])

    predictions = matcher.decode_batch(detectionEvents)

    numErrors = 0
    for shot in range(shots):
        actualForShot = observableFlips[shot]
        predictedForShot = predictions[shot]
        if not np.array_equal(actualForShot, predictedForShot):
            numErrors += 1

    if np.any(observableFlips):
        print("DEBUG")

    return numErrors

def countLogicalErrors_uf_rotated_single_shot(dem, detectionEvent, observableFlip) -> int:
    detCoords = dem.get_detector_coordinates()

    codeDistance = int(list(detCoords.values())[-1][-1])

    convCoords = {}
    for i in range(len(detCoords)):
        convCoords[i] = (detCoords[i][0] / 2 - 0.5, detCoords[i][1] / 2 - 0.5, detCoords[i][2])

    numErrors = 0

    code, decoder = initialize((codeDistance, codeDistance, codeDistance+1), "rotated", "unionfind", enabled_errors=["pauli"], faulty_measurements=True, initial_states=(0,0)
                                , plotting=False)
    
    triggeredDetectorCoords = []
    for detIndex in range(len(detectionEvent)):
        if detectionEvent[detIndex]:
            triggeredDetectorCoords.append(detCoords[detIndex])

    error_dict_for_qsurface = {}

    for i, err in enumerate(detectionEvent):
        if err == 1:
            error_dict_for_qsurface[convCoords[i]] = err

    output = run(code, decoder, error_rates = {"p_bitflip": 0.1, "p_phaseflip": 0.1}, decode_initial=False, custom_error_dict=error_dict_for_qsurface)
    matchings = output["matchings"]
    originalMatchings = matchings

    matchings = [str(m[0]).removeprefix("ex-").removeprefix("ex|").split('|')[0] for m in matchings if "ex" in str(m[0])]
    matchings = [(float(m.split(',')[0][1:]), float(m.split(',')[1][:-1])) for m in matchings]
    matchings = [(int((m[0] + 0.5) * 2), int((m[1] + 0.5) * 2)) for m in matchings]

    tmpParity = 0

    for m in matchings:
        if m[1] == 1 and m[0] % 2 == 1:
            tmpParity ^= 1

    if tmpParity != observableFlip:
        numErrors += 1
    #print(numErrors)

    return tmpParity, matchings, triggeredDetectorCoords