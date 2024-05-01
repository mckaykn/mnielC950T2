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
            for k, package in self.table[index]:
                if k == key:
                    return {
                        'address': package.address,
                        'deadline': package.delivery_deadline,
                        'city': package.city,
                        'zip_code': package.zip_code,
                        'weight': package.weight,
                        'status': package.status,
                        'delivery_time': package.timestamp,
                    }
        return None

    def delete(self, key):
        index = self._hash(key)
        if self.table[index] is not None:
            for i, (k, v) in enumerate(self.table[index]):
                if k == key:
                    del self.table[index][i]
                    return


packages_table = HashTable(50)
total_distance = 0


# A Package class to contain the format for a package data. Including package ID, Address, City, State, ZipCode,
# Delivery Deadline, Weight, Special Notes, Timestamp, Distance, Status, and a Status Tracker
# BIG O: O(1)
# Space Complexity: O(1)
class Package:
    def __init__(self, package_id, address, city, state, zip_code, delivery_deadline, weight, package_special_notes,
                 timestamp=None, distance=None, status=None, truck_number=None):
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
        self.truck_number = truck_number

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
               f"Status: {self.status}" \
               f"Truck Number: {self.truck_number}"


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
    truck_number = "Not Assigned"

    return Package(package_id, address, city, state, zip_code, delivery_deadline, weight, package_special_notes,
                   timestamp, package_distance, status, truck_number)


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


# Loads trucks for their first load of packages in the morning.
# BIG O: O(n)
# Space Complexity: O(n)
def load_morning_packages_into_trucks():
    for package_id, package in packages_table:
        i = 1
        if package.package_id in ["1", "12", "40", "4", "17", "31", "37", "30"]:
            truck_packages[i].append(package)
            package.status = "In route"
            package.status_tracker.append({package.status, package.timestamp})
            package.truck_number = i
            truck_package_counts[i] += 1
            continue
        i = 2
        if package.package_id in ["8", "13", "39", "14", "15", "16", "20", "19", "21", "34", "19", "7", "29", "22"]:
            truck_packages[i].append(package)
            package.status = "In route"
            package.status_tracker.append({package.status, package.timestamp})
            package.truck_number = i
            truck_package_counts[i] += 1
            continue


# Load packages into truck which need to be delivered after 9:05 AM and extra ones that can fit.
# which packages it wants to be delivered with, etc.
# BIG O: O(n)
# Space Complexity: O(1)
def load_mid_morning_packages_into_truck_one():
    # Load all packages that need to be delivered first, by their special note requirements and delivery deadlines.
    for package_id, package in packages_table:
        if package.package_id in ["32", "28", "6", "2", "25", "26", "33", "24", "23", "11"]:
            truck_packages[1].append(package)
            package.status = "In route"
            package.status_tracker.append({package.status, package.timestamp})
            package.truck_number = 1
            truck_package_counts[1] += 1


# Loads truck 2 at 10:20 AM when some packages receive their updates.
# Big O: O(n)
# Space Complexity: O(n)
def load_truck_2_on_return():
    for package_id, package in packages_table:
        if truck_package_counts[2] >= 16:
            break
        if package_id in ["9", "38", "36", "18", "5"]:
            truck_packages[2].append(package)
            package.status = "In route"
            package.status_tracker.append({package.status, package.timestamp})
            package.truck_number = 2
            truck_package_counts[2] += 1
            continue
        if package.status == "At Hub" and package.package_special_notes == "Can only be on truck 2":
            truck_packages[2].append(package)
            package.status = "In route"
            package.status_tracker.append({package.status, package.timestamp})
            package.truck_number = 2
            truck_package_counts[2] += 1
            continue
    for package_id, package in packages_table:
        if truck_package_counts[2] >= 16:
            break
        if package.status == "At Hub":
            truck_packages[2].append(package)
            package.status = "In route"
            package.status_tracker.append({package.status, package.timestamp})
            package.truck_number = 2
            truck_package_counts[2] += 1


# Create a route for trucks to deliver the packages they have. The route is created by finding the closest data point
# to the next by looping over the distance matrix with a min return. The package indices are passed in along with the
# distance matrix to create the optimized route.
# BIG O: O(n^2)
# Space Complexity: O(n)
def find_nearest_neighbor_route_and_distances(distance_matrix, remaining_packages):
    num_points = len(distance_matrix)
    unvisited = list(remaining_packages)
    route = [0]

    while unvisited:
        current_point = route[-1]
        valid_distances = []

        for point in unvisited:
            if point < current_point:
                # Use the symmetry property to get distances from the lower part of the matrix
                distance = distance_matrix[current_point][point]
            else:
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

    return route, distances


# Serves as a delivery function for entire program. Returns total distance and an object which
# acts as a start time for the next truck.
# BIG O: O(n^2)
# Space Complexity: O(1)
def deliver_packages(local_route, truck_number, distances, start_time):
    count = 0
    time_change = timedelta(minutes=0)
    total_distance = 0
    local_time = start_time
    for address_numeric in local_route:
        count += 1
        for package_id, package in packages_table:
            package_address_numeric = address_book.address_lookup(package.address)
            if package_address_numeric == address_numeric and package in truck_packages[truck_number]:
                package.status = "Delivered"
                package.truck_number = truck_number
                local_distance = 0
                for i in range(0, count):
                    local_distance += distances[i - 1]
                package.distance = local_distance
                time_change = timedelta(minutes=(local_distance / 18) * 60)
                package.timestamp = start_time + time_change
                package.status_tracker.append({package.status, package.timestamp})
                truck_packages[truck_number].remove(package)
                truck_package_counts[truck_number] -= 1
    total_distance += distance_array[local_route[-1]][0]
    total_distance += sum(distances)
    distances.clear()
    time = local_time + time_change
    return total_distance, time


load_morning_packages_into_trucks()
package_indices = []
# Each for loop is filling an array with the indices of the delivery locations for the correct truck.
# BIG O: O(n)
# Space complexity: O(m) where m is the number of packages meeting the specified conditions
for package_id, package in packages_table:
    if package.truck_number == 1:
        if package.status == "In route" and package.package_id != "9":
            package_indices.append(address_book.address_lookup(package.address))
optimized_route, distances = find_nearest_neighbor_route_and_distances(distance_array, package_indices)
distance, time = deliver_packages(optimized_route, 1, distances, datetime.strptime("2023-10-24 08:00:00",
                                                                                   "%Y-%m-%d %H:%M:%S"))
total_distance += distance
start_time_truck_one = time

package_indices.clear()
# Each for loop is filling an array with the indices of the delivery locations for the correct truck.
# BIG O: O(n)
# Space complexity: O(m) where m is the number of packages meeting the specified conditions
for package_id, package in packages_table:
    if package.truck_number == 2:
        if package.status == "In route" and package.package_id != "9":
            package_indices.append(address_book.address_lookup(package.address))
optimized_route, distances = find_nearest_neighbor_route_and_distances(distance_array, package_indices)
distance, time = deliver_packages(optimized_route, 2, distances, datetime.strptime("2023-10-24 08:00:00",
                                                                                   "%Y-%m-%d %H:%M:%S"))
total_distance += distance
start_time_truck_two = time
load_mid_morning_packages_into_truck_one()

package_indices_2 = []
# Each for loop is filling an array with the indices of the delivery locations for the correct truck.
# BIG O: O(n)
# Space complexity: O(m) where m is the number of packages meeting the specified conditions
for package_id, package in packages_table:
    if package.truck_number == 1:
        if package.status == "In route" and package.package_id != "9":
            package_indices_2.append(address_book.address_lookup(package.address))
optimized_route_2, distances = find_nearest_neighbor_route_and_distances(distance_array, package_indices_2)
if start_time_truck_one <= datetime.strptime("2023-10-24 09:05:00", "%Y-%m-%d %H:%M:%S"):
    start_time_truck_one = datetime.strptime("2023-10-24 09:05:00", "%Y-%m-%d %H:%M:%S")
distance, time = deliver_packages(optimized_route_2, 1, distances, start_time_truck_one)
total_distance += distance
start_time_truck_one = time
load_truck_2_on_return()
package_indices_3 = []
for package_id, package in packages_table:
    if package.package_id == "9":
        package.address = "410 S State St"
        package.city = "Salt Lake City"
        package.zip_code = "84111"
        package.state = "UT"
# Each for loop is filling an array with the indices of the delivery locations for the correct truck.
# BIG O: O(n)
# Space complexity: O(m) where m is the number of packages meeting the specified conditions
for package_id, package in packages_table:
    if package.truck_number == 2:
        if package.status == "In route":
            package_indices_3.append(address_book.address_lookup(package.address))
new_route, distances = find_nearest_neighbor_route_and_distances(distance_array, package_indices_3)
if start_time_truck_two <= datetime.strptime("2023-10-24 10:20:00", "%Y-%m-%d %H:%M:%S"):
    start_time_truck_two = datetime.strptime("2023-10-24 10:20:00", "%Y-%m-%d %H:%M:%S")
distance, time = deliver_packages(new_route, 2, distances, start_time_truck_two)
total_distance += distance
start_time_truck_two = time
print(f'Total distance: {total_distance}')
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


def display_package_data(package_id, package, timestamp):
    # Lookup package data using your Hash Table lookup function
    package_data = packages_table.lookup(str(package_id))

    if package_data is not None:
        status_at_time, delivered_time = check_package_status_at_time(package, timestamp)
        truck_number = package.truck_number
        if delivered_time:
            print(" {} | {} | {} | {} | {} | {} | {} | {} |".format(
                package_id,
                package_data.get('address', ''),
                package_data.get('deadline', ''),
                package_data.get('city', ''),
                package_data.get('zip_code', ''),
                truck_number,
                delivered_time,
                status_at_time
            ))
        else:
            print("Status at {}: {}".format(timestamp, status_at_time))
    else:
        print("Package data not found for ID: {}".format(package_id))


sorted_packages = sorted(packages_table, key=lambda x: int(x[0]), reverse=False)
check_user_intent = input("Would you like to check the Status of all packages by a certain time? Y/N")
if check_user_intent == ("y" or "Y"):
    timestamp_str = input("Enter the timestamp to check package statuses (2023-10-24 HH:MM:SS):")
    timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
    print("ID | Delivery Address | Delivery Deadline | City | Zip Code | Truck Number | Status Change Time | Status")
    for package_id, package in sorted_packages:
        display_package_data(package_id, package, timestamp)
else:
    key = input("To check a certain package please type the package ID:")
    try:
        print(packages_table.lookup(str(key)))
    except ValueError:
        print("Invalid ID. Please use only numerals 1, 2, 10, 20, ect.")

#     # Uses @check_package_status_at_time to print the statuses at the given time.
#     try:
#         # Convert the user input to a datetime object
#         timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
#
#         # Display package statuses at the specified time
#         print("\nPackage Statuses at {}: \n".format(timestamp_str))
#
#         # Sort packages by ID in ascending order
#         sorted_packages = sorted(packages_table, key=lambda x: int(x[0]), reverse=False)
#
#         for package_id, package in sorted_packages:
#             status_at_time, delivered_time = check_package_status_at_time(package, timestamp)
#             truck_number = package.truck_number
#             if delivered_time:
#                 print(
#                     "Package {}: {} at {} by Truck {}".format(package_id, status_at_time, delivered_time, truck_number))
#             else:
#                 print("Package {}: {}".format(package_id, status_at_time))
#     except ValueError:
#         print("Invalid timestamp format. Please use YYYY-MM-DD HH:MM:SS.")
# else:
#     key = input("To check a certain package please type the package ID:")
#     try:
#         print(packages_table.lookup(str(key)))
#     except ValueError:
#         print("Invalid ID. Please use only numerals 1, 2, 10, 20, ect.")
