import sys
import util

class Solution:

    def __init__(self):
        self.drivers = []
        self.loadByID ={}
        self.depot = util.Point(0,0)
        self.max_distance = 12*60

    def loadinputfile(self, file_path):
        loads = util.loadProblemFromFile(file_path)
        for load in loads:
            self.loadByID[int(load.id)] = load

    def caluclateSavings(self):
        savings = []
        for i in self.loadByID:
            for j in self.loadByID:
                if i != j:      
                    load1 = self.loadByID[i]
                    load2 = self.loadByID[j]      
                    key = (i, j)
                    # to caluclate saving from the paper
                    saving = (key, util.distanceBetweenPoints(load1.dropoff, self.depot) \
                                    + util.distanceBetweenPoints(self.depot, load2.pickup) \
                                    - util.distanceBetweenPoints(load1.dropoff, load2.pickup) - util.distanceBetweenPoints(load1.dropoff, load2.dropoff) )
                    
                    savings.append(saving)

        savings = sorted(savings, key = lambda x: x[1], reverse=True)
        #print(savings)

        return savings
    
    def distanceBetween(self, nodes):

        if not nodes:
            return 0.0
        
        distance = 0.0
        for i in range(len(nodes)):
            distance += nodes[i].delivery_distance
            if i != (len(nodes) - 1):
                distance += util.distanceBetweenPoints(nodes[i].dropoff, nodes[i+1].pickup)

        distance += util.distanceBetweenPoints(self.depot, nodes[0].pickup)
        distance += util.distanceBetweenPoints(nodes[-1].dropoff, self.depot)
        
        return distance

    def print_trips(self):

        for driver in self.drivers:
            print([int(load.id) for load in driver.route])

    def solveVRPPD(self):

        
        #Implementation of Clark-Wright Savings algorithm
        
        # calculate savings for each link
        savings = self.caluclateSavings()

        for link, _ in savings:

            load1 = self.loadByID[link[0]]
            load2 = self.loadByID[link[1]]

            # condition 1. chek if th fist loads are kept together 
            #check for top saving route 
            if not load1.assigned and not load2.assigned:

                # check constraints
                cost = self.distanceBetween([load1, load2])
                if cost <= self.max_distance:
                    driver = util.Driver()
                    driver.route = [load1, load2]
                    self.drivers.append(driver)
                    load1.assigned = driver
                    load2.assigned = driver

            # condition 2.  
            elif load1.assigned and not load2.assigned:

                driver = load1.assigned
                i = driver.route.index(load1)
                # if node is the last node of route
                if i == len(driver.route) - 1:
                    # check constraints
                    cost = self.distanceBetween(driver.route + [load2])
                    if load2.id == load1.id and load1 in driver.route:
                        load2_index = driver.route.index(load1) + 1
                        driver.route.insert(load2_index, load2)
                        load2.assigned = driver

            elif not load1.assigned and load2.assigned:

                driver = load2.assigned
                i = driver.route.index(load2)
                # if node is the first node of route
                if i == 0:
                    # check constraints
                    cost = self.distanceBetween([load1] + driver.route)
                    if cost <= self.max_distance:
                    # Check if load1 is a pickup and its corresponding dropoff is already in the route
                        if load1.id == load2.id and load2 in driver.route:
                            driver.route.insert(0, load1)
                            load1.assigned = driver


            # condition 3. 
            else:

                driver1 = load1.assigned
                i1 = driver1.route.index(load1)

                driver2 = load2.assigned
                i2 = driver2.route.index(load2)

                # if node1 is the last node of its route and node 2 is the first node of its route and the routes are different
                if (i1 == len(driver1.route) - 1) and (i2 == 0) and (driver1 != driver2):
                    cost = self.distanceBetween(driver1.route + driver2.route)
                    if cost <= self.max_distance:
                    # Check if load1 and load2 are pickup and dropoff pairs and they are consecutive in routes
                        if load2.id == load1.id and driver1.route[-1] == load1 and driver2.route[0] == load2:
                            driver1.route.extend(driver2.route)
                            for load in driver2.route:
                                load.assigned = driver1
                            self.drivers.remove(driver2)

        # Assign all unassigned drivers to individual routes  
        # ## we may need to apply tabu or GA algorithm for assigning unassigned routes     
        for load in self.loadByID.values():
            if not load.assigned:
                driver = util.Driver(0, [])
                driver.route.append(load)
                self.drivers.append(driver)
                load.assigned = driver
        
                
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python solution.py <file_path>")
        sys.exit(1)
    file_path = sys.argv[1]
    solution = Solution()
    solution.loadinputfile(file_path)
    solution.solveVRPPD()
    solution.print_trips()
