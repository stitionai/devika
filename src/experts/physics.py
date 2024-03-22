class PhysicsFunctions:
    def __init__(self):
        pass

    def calculate_force(self, mass, acceleration):
        return mass * acceleration

    def calculate_velocity(self, initial_velocity, acceleration, time):
        return initial_velocity + acceleration * time

    def calculate_displacement(self, initial_velocity, time, acceleration):
        return initial_velocity * time + 0.5 * acceleration * time ** 2

