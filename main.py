# McKay Nielson, WGU ID: 002559933
import csv
from datetime import datetime, timedelta


# A HashTable class made from scratch to hold package data. Contains an insert, lookup, and delete function
# BIG O: O(1) for average case (assuming a good hash function), O(n) for worst case (collision resolution)
# Space Complexity: O(n)
class HashTable:
    def __init__(self, size):
        self.size = size
        self.table = [None] * size

    def __iter__(self):
        # Iterate through each item in the table
        for bucket in self.table:
            if bucket is not None:
                for key, value in bucket:
                    yield key, value

    def _hash(self, key):
        return hash(key) % self.size

    def insert(self, key, value):
        index = self._hash(key)
        if self.table[index] is None:
            self.table[index] = [(key, value)]
        else:
            for i, (k, v) in enumerate(self.table[index]):
                if k == key:
                    self.table[index][i] = (key, value)
                    return
            self.table[index].append((key, value))

    def lookup(self, key):
        index = self._hash(key)
        if self.table[index] is not None:
            for k, v in self.table[index]:
                if k == key:
                    return v
        return None

    def delete(self, key):
        index = self._hash(key)
        if self.table[index] is not None:
            for i, (k, v) in enumerate(self.table[index]):
                if k == key:
                    del self.table[index][i]
                    return


packages_table = HashTable(50)


# A Package class to contain the format for a package data. Including package ID, Address, City, State, ZipCode,
# Delivery Deadline, Weight, Special Notes, Timestamp, Distance, Status, and a Status Tracker
# BIG O: O(1)
# Space Complexity: O(1)
class Package:
    def __init__(self, package_id, address, city, state, zip_code, delivery_deadline, weight, package_special_notes,
                 timestamp=None, distance=None, status=None):
        self.package_id = package_id
        self.address = address
        self.city = city
        self.state = state
        self.zip_code = zip_code
        self.delivery_deadline = delivery_deadline
        self.weight = weight
        self.package_special_notes = package_special_notes
        self.timestamp = timestamp
        self.distance = distance
        self.status = status
        self.status_tracker = [{status, timestamp}]

    def __str__(self):
        return f"Package ID: {self.package_id}\n" \
               f"Address: {self.address}\n" \
               f"City: {self.city}\n" \
               f"State: {self.state}\n" \
               f"ZIP Code: {self.zip_code}\n" \
               f"Delivery Deadline: {self.delivery_deadline}\n" \
               f"Weight in Kilos: {self.weight}\n" \
               f"Special Notes: {self.package_special_notes}\n" \
               f"Timestamp: {self.timestamp}\n" \
               f"Distance: {self.distance}\n" \
               f"Status: {self.status}"


# Creates a package object from the passed in csv row from WGUPSpackage.csv
# BIG O: O(1)
# Space Complexity: O(1)
def create_package_from_csv_row(row):
    package_id = row[0]  # Adjust the index to match the position of package_id in your CSV
    address = row[1]  # Adjust the index for the address column
    city = row[2]  # Adjust the index for the city column
    state = row[3]  # Adjust the index for the state column
    zip_code = row[4]  # Adjust the index for the zip_code column
    delivery_deadline = row[5]  # Adjust the index for the delivery_deadline column
    weight = row[6]
    package_special_notes = row[7]
    timestamp = datetime.strptime("2023-10-24 08:00:00", "%Y-%m-%d %H:%M:%S")  # initialize the time to 8:00am
    package_distance = 0.0  # initialize the distance to 0.0
    status = "At Hub"

    return Package(package_id, address, city, state, zip_code, delivery_deadline, weight, package_special_notes,
                   timestamp, package_distance, status)


# Load package data into packages_table HashTable
# BIG O: O(n)
# Space Complexity: O(n)
with open('Helper/WGUPSpackage.csv', 'r', encoding='utf-8') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    for row in csv_reader:
        package = create_package_from_csv_row(row)
        # Insert the Package object into the HashTable with the package_id as the key
        packages_table.insert(package.package_id, package)

distance_array = []
# Load distance data into distance_array
with open('Helper/WGUPSDistance.csv', 'r') as file:
    csv_reader = csv.reader(file)

    for row in csv_reader:
        # Initialize a list for the current row
        current_row = []
        for cell in row:
            if cell.strip():  # Check if the cell is not empty or contains only whitespace
                current_row.append(float(cell))
            else:
                current_row.append(None)  # Replace null values with None or any other suitable value
        distance_array.append(current_row)


# A Class containing each data object in the WGUPSaddress.csv file. Also contains a counter given to each address
# and a lookup function passing in the address and returning the associated counter.
# BIG O: O(1)
# Space Complexity: O(n)
class AddressBook:
    def __init__(self):
        self.address_dict = {}
        self.counter = 0

    def add_address(self, address):
        numeric_value = self.counter
        self.address_dict[address] = numeric_value
        self.counter += 1

    def address_lookup(self, address):
        return self.address_dict.get(address)


address_book = AddressBook()
# Create an address Book
with open('Helper/WGUPSaddress.csv', 'r') as csv_file:
    csv_reader = csv.reader(csv_file)
    for row in csv_reader:
        address = row[0].strip()
        address_book.add_address(address)

# Create two lists of packages, one for each truck
truck_packages = {1: [], 2: []}
truck_package_counts = {1: 0, 2: 0}
# Stores distances of the route
distances = []
total_distance = 0


# Load packages into truck which are priority, i.e. delivery deadline is before noon or contains special notes about
# which packages it wants to be delivered with, etc.
# BIG O: O(n)
# Space Complexity: O(1)
def load_packages_into_trucks():
    # Load all packages that need to be delivered first, by their special note requirements and delivery deadlines.
    for package_id, package in packages_table:
        i = 1
        trucks_are_full = False
        if truck_package_counts[1] == 16:
            i = 2
        if truck_package_counts[2] == 16:
            trucks_are_full = True
            break
        if package.status == "At Hub" and package.delivery_deadline == "10:30 AM" and package.package_special_notes == "":
            truck_packages[i].append(package)
            truck_package_counts[i] += 1
            package.status = "In route"
            package.status_tracker.append({package.status, package.timestamp})
            continue
        if package.status == "At Hub" and package.delivery_deadline == "10:30 AM" and package.package_special_notes != "":
            if (package.package_special_notes in
                    ["Must be delivered with 15, 19",
                     "Must be delivered with 13, 19",
                     "Must be delivered with 13, 15"]):
                package.status = "In route"
                package.status_tracker.append({package.status, package.timestamp})
                truck_packages[2].append(package)
                truck_package_counts[2] += 1
                continue
        if package.status == "At Hub":
            if package_id == "13" or package_id == "15" or package_id == "19":
                truck_package_counts[2] += 1
                package.status = "In route"
                package.status_tracker.append({package.status, package.timestamp})
                truck_packages[2].append(package)
                continue
            if package.package_special_notes == "Can only be on truck 2":
                truck_package_counts[2] += 1
                package.status = "In route"
                package.status_tracker.append({package.status, package.timestamp})
                truck_packages[2].append(package)
                continue
            if package.status == "At Hub" and trucks_are_full is False:
                if package.package_special_notes == "":
                    truck_packages[i].append(package)
                    package.status = "In route"
                    package.status_tracker.append({package.status, package.timestamp})
                    truck_package_counts[i] += 1


# Create a route for trucks to deliver the packages they have. The route is created by finding the closest data point
# to the next by looping over the distance matrix with a min return.
# BIG O: O(n^2)
# Space Complexity: O(n)
def find_nearest_neighbor_route(distance_matrix):
    num_points = len(distance_matrix)
    unvisited = list(range(num_points))
    route = [0]
    unvisited.remove(0)

    while unvisited:
        current_point = route[-1]
        valid_distances = [(point, distance_matrix[point][current_point]) for point in unvisited if
                           distance_matrix[point][current_point] is not None]

        if valid_distances:
            nearest_point, distance = min(valid_distances, key=lambda x: x[1])
            distances.append(distance)
            route.append(nearest_point)
            unvisited.remove(nearest_point)
        else:
            nearest_point = unvisited.pop(0)
            route.append(nearest_point)

    return route


# Deliver packages for each truck along their respective routes, comparing each point stopped at with the packages
# given address and updating the status, timestamp, and distance each time they are delivered.
# BIG O: O(n^2)
# Space Complexity: O(1)
def deliver_first_packages(truck_packages, distance_array, address_book):
    routes = {}
    for truck_number, packages in truck_packages.items():
        optimized_route = find_nearest_neighbor_route(distance_array)  # Use the nearest-neighbor algorithm
        routes[truck_number] = optimized_route

    for truck_number, route in routes.items():
        count = 0
        for (address_numeric) in route:
            address = list(address_book.address_dict.keys())[
                list(address_book.address_dict.values()).index(address_numeric)]
            count += 1
            for package_id, package in packages_table:
                if address_book.address_lookup(package.address) == address_numeric \
                        and package in truck_packages[truck_number]:
                    package.status = "Delivered"
                    local_distance = 0
                    for i in range(0, count):
                        local_distance += distances[i]
                    package.distance = local_distance
                    time_change = timedelta(minutes=(local_distance / 18) * 60)
                    package.timestamp = package.timestamp + time_change
                    package.status_tracker.append({package.status, package.timestamp})
                    truck_packages[truck_number].remove(package)


# Loads the final packages needed to be delivered into one truck.
# BIG O: O(n)
# Space Complexity: O(1)
def load_last_packages_into_truck_one():
    for package_id, package in packages_table:
        i = 1
        processed = False
        if package.status == "At Hub":
            time_change = timedelta(minutes=(total_distance / 18) * 60)
            package.timestamp = package.timestamp + time_change
            if package.package_special_notes == "Delayed on flight---will not arrive to depot until 9:05 am":
                time_string = "09:05:00"
                string_to_time = datetime.strptime(time_string, "%H:%M:%S").time()
                if datetime.time(package.timestamp) > string_to_time:
                    if truck_package_counts[i] < 16:
                        truck_packages[i].append(package)
                        truck_package_counts[i] += 1
                        package.status = "In route"
                        package.status_tracker.append({package.status, package.timestamp})
                        processed = True
            # Reroute package with "Wrong address listed" if the time is after 10:20 AM.
            if not processed and package.package_special_notes == "Wrong address listed":
                initial_time_string = "10:20:00"
                string_to_time = datetime.strptime(initial_time_string, "%H:%M:%S").time()
                if datetime.time(package.timestamp) > string_to_time:
                    package.address = "410 S State St"
                    package.city = "Salt Lake City"
                    package.state = "UT"
                    package.zip_code = 84111
                    if truck_package_counts[i] < 16:
                        truck_packages[i].append(package)
                        truck_package_counts[i] += 1
                        package.status = "In route"
                        package.status_tracker.append({package.status, package.timestamp})
                        processed = True
            if not processed:
                truck_packages[1].append(package)
                package.status = "In route"
                package.status_tracker.append({package.status, package.timestamp})
                truck_package_counts[i] += 1


# Creates a new route consisting of only the remaining packages addresses.
# BIG O: O(n^2)
# Space Complexity: O(n)
def find_nearest_neighbor_route_with_final_packages(distance_matrix, remaining_packages):
    num_points = len(distance_matrix)
    unvisited = list(remaining_packages)
    route = [0]

    while unvisited:
        current_point = route[-1]
        valid_distances = []
        for point in unvisited:
            distance = distance_matrix[point][current_point]
            if distance is not None:
                valid_distances.append((point, distance))

        if valid_distances:
            nearest_point, distance = min(valid_distances, key=lambda x: x[1])
            distances.append(distance)
            route.append(nearest_point)
            unvisited.remove(nearest_point)
        else:
            nearest_point = unvisited.pop(0)
            route.append(nearest_point)

    return route


# Delivers the final packages loaded into truck one. Updates the packages when delivered. Calculates total distance.
# BIG O: O(n^2)
# Space Complexity: O(1)
def deliver_final_packages(local_route):
    count = 0
    for (address_numeric) in local_route:
        count += 1
        for package_id, package in packages_table:
            package_address_numeric = address_book.address_lookup(package.address)
            if package_address_numeric == address_numeric and package in truck_packages[1]:
                package.status = "Delivered"
                local_distance = 0
                for i in range(0, count):
                    local_distance += distances[i]
                new_total_distance = local_distance + total_distance
                package.distance = new_total_distance
                time_change = timedelta(minutes=(local_distance / 18) * 60)
                package.timestamp = package.timestamp + time_change
                package.status_tracker.append({package.status, package.timestamp})
                truck_packages[1].remove(package)
    new_total_distance = new_total_distance + distance_array[local_route[-1]][0]
    print(f'Total distance: {new_total_distance}')


load_packages_into_trucks()
deliver_first_packages(truck_packages, distance_array, address_book)
total_distance = sum(distances) + 6.4
# Create a list to store indices of remaining packages
remaining_packages_indices = []
# Iterate through the packages and add the indices of At Hub packages to the list
for package_id, package in packages_table:
    if package.status == "At Hub" and package_id != "9":
        remaining_packages_indices.append(
            address_book.address_lookup(package.address))
    if package.package_id == "9":
        remaining_packages_indices.append(19)
load_last_packages_into_truck_one()
new_route = find_nearest_neighbor_route_with_final_packages(distance_array, remaining_packages_indices)

deliver_final_packages(new_route)
for package_id, package in packages_table:
    if package.status != "Delivered":
        print("package not delivered", package)

print("End Of Day")


# Method used to return the correct status of packages compared to the passed in timestamp that the user provides.
# BIG O: O(n)
# Space Complexity: O(1)
def check_package_status_at_time(package, timestamp):
    for entry in reversed(package.status_tracker):
        if isinstance(entry, (tuple, set)) and len(entry) == 2:
            # Check if the entry is an iterable with two elements
            status_time, status = entry
            if isinstance(status_time, datetime) and status_time <= timestamp:
                return status, status_time
            elif isinstance(status, datetime) and status <= timestamp:
                return status_time, status

    return "Status not available at {}".format(timestamp), None

timestamp_str = input("Enter the timestamp to check package statuses (2023-10-24 HH:MM:SS):")
# Uses @check_package_status_at_time to print the statuses at the given time.
try:
    # Convert the user input to a datetime object
    timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")

    # Display package statuses at the specified time
    print("\nPackage Statuses at {}: \n".format(timestamp_str))

    # Sort packages by ID in ascending order
    sorted_packages = sorted(packages_table, key=lambda x: int(x[0]), reverse=False)

    for package_id, package in sorted_packages:
        status_at_time, delivered_time = check_package_status_at_time(package, timestamp)
        if delivered_time:
            print("Package {}: {} at {}".format(package_id, status_at_time, delivered_time))
        else:
            print("Package {}: {}".format(package_id, status_at_time))

except ValueError:
    print("Invalid timestamp format. Please use YYYY-MM-DD HH:MM:SS.")
