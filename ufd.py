from surface_code import SurfaceCode

testCode = SurfaceCode(distance=3, px_error=0.1, pz_error=0.1, meas_error=0.1)
print(testCode)

print("Generating error...")

testCode.generateError()
print(testCode)