import random
import time
import threading

def get_random_int(min_val, max_val):
    return random.randint(min_val, max_val)

class User:
    def __init__(self, name):
        self.name = name
        self.assigned_resource = None
        self.resource_id = None
        self.time_required = None

    def set_request(self, resources):
        self.resource_id = get_random_int(1, len(resources))
        self.time_required = get_random_int(1, 30)

    def request_resource(self, resources):
        resource = resources[self.resource_id - 1]
        self.assigned_resource = resource
        resource.assign_user(self, self.time_required)

class Resource:
    def __init__(self, resource_id):
        self.id = resource_id
        self.user = None
        self.time_left = 0
        self.waiting_queue = []

    def assign_user(self, user, time_required):
        if self.user is None:
            self.user = user
            self.time_left = time_required
            print(f"Resource {self.id} is now being used by {user.name} for {time_required} seconds.")
        else:
            self.waiting_queue.append({'user': user, 'time': time_required})
            print(f"{user.name} is added to the waiting list for Resource {self.id}.")
            self.display_waiting_users()

    def process_resource(self):
        if self.user:
            self.time_left -= 1
            if self.time_left <= 0:
                print(f"Resource {self.id} is now free. {self.user.name} has finished.")
                self.user = None
                if self.waiting_queue:
                    next_user = self.waiting_queue.pop(0)
                    print(f"{next_user['user'].name} is now using Resource {self.id}.")
                    self.assign_user(next_user['user'], next_user['time'])

    def display_status(self):
        if self.user:
            print(f"Resource {self.id} is currently used by {self.user.name}, {self.time_left}s left.")
        else:
            print(f"Resource {self.id} is free.")
        self.display_waiting_users()

    def display_waiting_users(self):
        if self.waiting_queue:
            names = ', '.join([entry['user'].name for entry in self.waiting_queue])
            print(f"Users waiting for Resource {self.id}: {names}")

def simulate():
    num_resources = get_random_int(1, 30)
    num_users = get_random_int(1, 30)

    resources = [Resource(i + 1) for i in range(num_resources)]
    users = [User(f"User {i + 1}") for i in range(num_users)]

    # Pre-generate requests
    for user in users:
        user.set_request(resources)

    # Sort users by user number (FIFO)
    users.sort(key=lambda u: int(u.name.split()[1]))

    for user in users:
        user.request_resource(resources)

    simulation_time = 0

    while True:
        print(f"\nSimulation Time: {simulation_time}s")
        for res in resources:
            res.display_status()
        for res in resources:
            res.process_resource()

        if all(res.user is None and not res.waiting_queue for res in resources):
            print("\nAll resources are free. Simulation complete.")
            break

        simulation_time += 1
        time.sleep(1)

simulate()
