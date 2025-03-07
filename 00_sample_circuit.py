import stim
import utils

if __name__ == "__main__":
    circuit = stim.Circuit()

    circuit.append("H", [0])
    circuit.append("TICK")

    circuit.append("CNOT", [0, 1])
    circuit.append("X_ERROR", [0, 1], 0.2)
    circuit.append("TICK")

    circuit.append("M", [0, 1])
    circuit.append("DETECTOR", [stim.target_rec(-1), stim.target_rec(-2)])

    print(circuit.diagram())

    # Sampling the circuit
    # sampler = circuit.compile_sampler()
    # print(sampler.sample(shots=10))

    # Sampling the error-detecting circuit
    sampler = circuit.compile_detector_sampler()
    samplingList = sampler.sample(shots=10**6).tolist()
    #print(samplingList)

    errorRate = samplingList.count([True]) / len(samplingList)
    print(f"Error rate: {errorRate}")

    utils.saveSVG(circuit, "timeline-svg", "pictures/00_sample_circuit_timeline")   
    utils.saveSVG(circuit, "timeslice-svg", "pictures/00_sample_circuit_timeslice")