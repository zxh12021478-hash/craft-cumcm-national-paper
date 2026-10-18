# Candidate draft calculation, supplied for audit, not a trusted reference.
def battery_energy(charge, discharge):
    energy = 0.0
    states = []
    for c, d in zip(charge, discharge):
        energy += 0.9*c - 0.9*d
        states.append(energy)
    return states
if __name__ == '__main__':
    print(battery_energy([1,0,0], [0,2,0]))
