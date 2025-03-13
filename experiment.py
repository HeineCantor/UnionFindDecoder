import experimental_setup.accuracy as accuracy

if __name__ == "__main__":
    stats = accuracy.accuracyByDistance()

    with open("results.txt", "w") as f:
        f.write(str(stats).replace('),','),\n'))