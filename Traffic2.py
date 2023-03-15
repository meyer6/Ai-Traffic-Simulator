import pyglet, copy, pickle, neat, os, random
from pyglet import shapes
import pyglet.window
from GeneralFunctions import pythag, getHorizontalData, getVerticalData, getLength, getEllipseData

class Car:
    def __init__(self, journey, trafficLights, type):
        self.i = 1
        self.journey = journey
        self.trafficLights = trafficLights
        self.type = type
        self.blocked = [False, 0]
        self.sameStart = []

        # Initializes the car - dimensions and color
        x, y, t = self.journey[0][1](self.i)
        if self.type == "Truck":
            self.car = shapes.Rectangle(x=x, y=y, width=CAR_WIDTH * 2, height=CAR_HEIGHT, color=(225, 248, 250))
        elif self.type == "Motorbike":
            self.car = shapes.Rectangle(x=x, y=y, width=CAR_WIDTH * 0.7, height=CAR_HEIGHT * 0.7, color=(250, 225, 225))
        else:
            self.car = shapes.Rectangle(x=x, y=y, width=CAR_WIDTH, height=CAR_HEIGHT, color=(246, 246, 246))
        self.car.anchor_y = self.car.height//2
        self.car.anchor_x = self.car.width//2

    def update(self, cars, time):
        # Slows a truck down during corners
        if self.type == "Truck" and type(self.car.x) is not float or self.type == "Truck" and type(self.car.x) is float and time % 3 != 0 or self.type != "Truck":
            
            # Will stop the car if it is blocked
            self.blocked[0] = self.checkIfBlocked(cars)
            if self.blocked[0] == False:

                # Moves the car forward
                self.i += 1 

                # Checks and moves the car onto a new section
                if self.i > self.journey[0][0]:
                    self.journey.pop(0)
                    self.i = 1

                # End of journey
                if len(self.journey) == 0:
                    return False
                
                # Calculates the new cars position and angle
                x, y, t = self.journey[0][1](self.i)
                self.car.position, self.car.rotation = (x, y), t

    def checkIfBlocked(self, cars):
        # Implements acceleration - will stop for 20 iterations and immediatly accelerate instead of a gradual acceleration
        if self.blocked[0]:
            self.blocked[1] = (self.blocked[1] + 1) % 20
            if self.blocked[1] != 0:
                return True
        
        # Prevents collisions between cars
        section = 0
        for di in range(5, 86, 20):
            if di == 85:
                di = 80
            tempi = self.i + di

            while len(self.journey) - section != 1 and tempi > self.journey[section][0]:
                section += 1
                tempi = tempi - self.journey[section][0]

            if len(self.journey) - section != 1:
                x, y, t = self.journey[section][1](tempi)
                for car in cars:
                    if di >= 80 and car.type == "Truck" or di <= 65:
                        if car not in self.sameStart and car.journey[0][0] == self.journey[0][0]:
                            self.sameStart.append(car)

                        if car != self:
                            x1, y1, t = car.journey[0][1](car.i)
                            distance = pythag(y1-y, x1-x)

                            if di == 5:
                                if car.journey[-1] == self.journey[-1] and distance < 40:
                                    return True
                            elif di >= 80 and car in self.sameStart and distance < 10:
                                return True
                            elif car in self.sameStart and di < 45 and distance < 40 or car not in self.sameStart and distance < 20:
                                return True
                            elif car.journey[0][0] > car.i + 25 and car.blocked[0] == False:
                                x1, y1, t = car.journey[0][1](car.i + 25)
                                if pythag(y1-y, x1-x) < 25:
                                    return True

        # Stops the cars at traffic lights
        for trafficLight in self.trafficLights:
            if self.type != "Truck":
                if trafficLight[1] != 0 and trafficLight[0] == self.journey[0] and abs(self.journey[0][0] - self.i - 40) < 5:
                    return True
            elif self.type == "Truck":
                if trafficLight[1] != 0 and trafficLight[0] == self.journey[0] and abs(self.journey[0][0] - self.i - 55) < 5:
                    return True
        return False

class PedestrianManager:
    def __init__(self, waitingTime, trafficLights):
        self.waitingTime = waitingTime
        self.trafficLights = trafficLights

        # Defines the number of pedestrians waiting
        self.pedestrianNums = [0 for _ in range(len(self.trafficLights))]
        self.pedestrianTimes = [random.randint(0, 300) for _ in range(len(self.trafficLights))]

    def managePedestrians(self, time, pedestrianTime):
        # Spawns in pedestrians
        for i, pedestrianTime2 in enumerate(self.pedestrianTimes):
            if time - pedestrianTime2 >= 800:
                self.pedestrianNums[i] += 1
                self.pedestrianTimes[i] = time

        # Removes pedestrians after they have crossed the road
        if time - pedestrianTime == 480:
            self.waitingTime[1] += sum(self.pedestrianNums)
            self.pedestrianNums = [0 for _ in range(len(self.trafficLights))]
            self.pedestrianTimes = [time + random.randint(0, 300) for _ in range(len(self.trafficLights))]

        self.waitingTime[0] += sum(self.pedestrianNums)

class CarManager:
    def __init__(self, waitingTime, trafficLights):
        self.cars = []
        self.trafficLights = trafficLights

        # Defines the rate at which vehicles arrive and the last time a vehicle of a given route was spawned
        self.routesRates = [[1750, 1750], [1120, 1120], [1120, 1120], [1020, 1020], [1020, 1020], [360, 360], [870, 870], [360, 360], [870, 870]]
        self.routeTimes = [random.randint(0, 200) for _ in range(len(routes))]

        # Defines the number of cars waiting at a traffic light
        self.trafficNums = [0 for _ in range(len(self.trafficLights))]

        # Defines the cars which are pending to be spawned
        self.backLog = []

        self.waitingTime = waitingTime

    def manageCars(self, time):
        # Varies the rate at which cars arrive
        if time % 5000 == 0:
            self.varyCarRates()

        self.trafficNums = [0 for _ in range(len(self.trafficLights))]
        self.updateCars(time)
        self.spawnCars(time)     
        self.calculateTrafficNums()
        self.waitingTime[0] += len(self.backLog) + len(self.cars)

    def varyCarRates(self):
        # Varies the amount of time it takes for cars to arrive
        for index in range(len(self.routesRates)):
            multiplier = 1 + 0.35 * ((random.randint(-100, 100) / 100) ** 3)
            self.routesRates[index][1] = self.routesRates[index][0] * multiplier

    def updateCars(self, time):
        # Updates the cars - removes if done
        for car in self.cars:
            if car.update(self.cars, time) == False:
                self.waitingTime[1] += 1
                self.cars.remove(car)
            else:
                self.setTrafficNums(car)

    def calculateTrafficNums(self):
        # Calculates the number of cars in the backlog waiting at each traffic light
        for log in self.backLog:
            for i, trafficLight in enumerate(self.trafficLights):
                if routes[log[0]][0] == trafficLight[0]:
                    if log[1] == "Truck":
                        self.trafficNums[i] += (len(self.backLog) - self.backLog.index(log)) * 2
                    else:
                        self.trafficNums[i] += len(self.backLog) - self.backLog.index(log)

    def setTrafficNums(self, car):
        # Determines if the car is waiting at a traffic light 
        for i, trafficLight in enumerate(self.trafficLights):
            if car.journey[0] == trafficLight[0]: 
                self.trafficNums[i] += 1
                break

    def spawnCars(self, time):
        # Spawns cars in the backlog
        for log in self.backLog:
            if self.checkIfBlocked(log[0]) == False:
                self.cars.append(Car(copy.deepcopy(routes[log[0]]), self.trafficLights, log[1]))
                self.backLog.remove(log)

        # Spawns new cars
        for index, lastTime in enumerate(self.routeTimes):
            if time - lastTime > self.routesRates[index][1]:

                # Creates random chance of getting different types of vehicles
                a = random.randint(1, 100)
                if a <= 91:
                    type = "Car"
                elif a <= 94:
                    type = "Motorbike"
                else:
                    type = "Truck"

                if self.checkIfBlocked(index) == False: 
                    self.cars.append(Car(copy.deepcopy(routes[index]), self.trafficLights, type))
                else:
                    self.backLog.append([index, type])

                self.routeTimes[index] = time

    def checkIfBlocked(self, index):
        # Detects if there is a car blocking the spawn point
        x, y, t = routes[index][0][1](1) 
        for car in self.cars: 
            x1, y1, t = car.journey[0][1](car.i) 
            if pythag(x1-x, y1-y) <= 40: 
                return True
        return False

class TrafficLightManager:
    def __init__(self, trafficLights):
        self.changes = []
        self.trafficLights = trafficLights
        self.setGreenTimes = []
        self.setRedTimes = []
        self.pedestrianTime = -500

    def pedestrianPass(self, time):
        # Sets all traffic lights to red and lets pedestrians pass
        for i in range(4):
            self.setRed(i, time, True)

        self.pedestrianTime = time

    def setRed(self, index, time, certain = False):
        # Sets a minimum time a light must be green for
        for greenTime in self.setGreenTimes:
            if greenTime[0] == index and time - greenTime[1] <= 500 and certain == False:
                return False

        # Switches the traffic light to yellow
        if self.trafficLights[index][1] == 0:
            self.trafficLights[index][1] = 1
            self.changes.append([index, time])
            self.setRedTimes.append([index, time])

    def setGreen(self, index, time):
        # Prevents lights from going green while pedestrians are passing
        if time - self.pedestrianTime <= 500:
            return False

        # Sets a minimum time a light must be red for
        for redTime in self.setRedTimes:
            if redTime[0] == index  and time - redTime[1] <= 250:
                return False
    
        # Prevents adjancent traffic lights from going on at the same time
        if index == 0 or index == 1:
            if self.trafficLights[2][1] != 2 or self.trafficLights[3][1] != 2:
                return False
        if index == 2 or index == 3:
            if self.trafficLights[0][1] != 2 or self.trafficLights[1][1] != 2:
                return False  

        # Sets traffic light to green
        if self.trafficLights[index][1] == 2:
            self.setGreenTimes.append([index, time])
            self.trafficLights[index][1] = 0

    def update(self, time):
        # Allows light to be switched to red
        for greenTime in self.setGreenTimes:
            if time - greenTime[1] >= 300:
                self.setGreenTimes.remove(greenTime)

        # Allows light to be switched to green
        for redTime in self.setRedTimes:
            if time - redTime[1] >= 300:
                self.setRedTimes.remove(redTime)

        # Changes yellow to red after a certain time
        for change in self.changes:
            if time - change[1] >= 150:
                self.trafficLights[change[0]][1] = 2
                self.changes.remove(change)

class RoundRobinAi:
    def __init__(self):
        self.lastTime = 0
        self.turn = 0

    def run(self, trafficManager, time):
        # Turns light green
        if time - self.lastTime >= 175:
            trafficManager.setGreen(self.turn, time)
            trafficManager.setGreen(self.turn + 1, time)

        # Lets pedestrians pass
        if time - self.lastTime == 1749 and self.turn == 2:
            trafficManager.pedestrianPass(time)

        # Turns light red
        if time - self.lastTime >= 1750:
            trafficManager.setRed(self.turn, time)
            trafficManager.setRed(self.turn + 1, time)
            self.turn = (self.turn + 2) % 4
            self.lastTime = time

class Simulation:
    def __init__(self, ai, trafficLights):
        self.ai = ai
        # self.ai = RoundRobinAi()
        self.time = 0

        self.co2 = "0"
        self.waitingTimeData = "0"
        self.energyWasted = "0"

        # Defines total number of car iterations and total cars passed
        self.waitingTime = [1, 1]

        self.trafficLights = trafficLights
        # Sets traffic lights to red initially
        for i in range(len(self.trafficLights)):
            self.trafficLights[i][1] = 2

        # Sets up the car, pedestrian and traffic light managers
        self.carManager = CarManager(self.waitingTime, self.trafficLights)
        self.pedestrianManager = PedestrianManager(self.waitingTime, self.trafficLights)
        self.trafficManager = TrafficLightManager(self.trafficLights)

    def update(self):
        self.time += 1

        # Ends simulation after a certain number of iterations
        if self.time >= 50000:
            pyglet.app.exit()

        # Updates the cars and traffic lights
        self.carManager.manageCars(self.time)
        self.pedestrianManager.managePedestrians(self.time, self.trafficManager.pedestrianTime)
        self.runAi()
        self.trafficManager.update(self.time)

        self.calculateData()

    def runAi(self):
        # self.ai.run(self.trafficManager, self.time) # Uncomment for Round Robin system

        if self.time % 150 == 0:
            # Gives ai input data and recieves output
            output = self.ai.activate((
                    self.carManager.trafficNums[0], self.trafficLights[0][1],
                    self.carManager.trafficNums[1], self.trafficLights[1][1],
                    self.carManager.trafficNums[2], self.trafficLights[2][1],
                    self.carManager.trafficNums[3], self.trafficLights[3][1],
                    sum(self.pedestrianManager.pedestrianNums)
                ))
            if output[4] >= 0.90 and self.time - self.trafficManager.pedestrianTime >= 2450:
                self.trafficManager.pedestrianPass(self.time)

            # Decodes and performs output of ai
            elif output[0] + output[1] > output[2] + output[3]:
                self.trafficManager.setRed(2, self.time)
                self.trafficManager.setRed(3, self.time)
                for i in range(2):
                    if output[i] > 0:
                        self.trafficManager.setGreen(i, self.time)
            else:
                self.trafficManager.setRed(0, self.time)
                self.trafficManager.setRed(1, self.time)
                for i in range(2, 4):
                    if output[i] > 0:
                        self.trafficManager.setGreen(i, self.time)

    def calculateData(self):
        # Calculates the relevant data
        if self.time % 200 == 0:
            self.co2 = str(int(self.waitingTime[0] * 0.012 / 40 / 60 * 1000))
            self.waitingTimeData = str(round((self.waitingTime[0] / self.waitingTime[1]) / 40, 1))
            self.energyWasted = str(int((self.waitingTime[0] / 40) * 1.54))

class Window(pyglet.window.Window):
    def __init__(self, ai):
        super().__init__()
        # Sets screen size to 500 by 500 px
        self.set_size(500, 500) 

        # Defines the sections which traffic lights are at and there current state 0 - green, 1 - yellow, 2 - red
        self.trafficLights = [[sections[0], 2],
                            [sections[2], 2], 
                            [sections[5], 2], 
                            [sections[6], 2]]
        self.roadSetup()

        # Creates the simulation
        self.simulation = Simulation(ai, self.trafficLights)

    def roadSetup(self):
        self.batch = pyglet.graphics.Batch()
        self.bg = []

        # Draws Roads
        for section in sections:
            for i in range(1, int(section[0])):
                x, y, t = section[1](i)
                self.bg.append(shapes.Circle(x, y, ROAD_WIDTH, color=ROAD_COLOUR, batch=self.batch))

        # Draws lines on roads
        for route in routes:
            for a in range(0, len(route), 2):
                for i in range(1, int(route[a][0]), 27):
                    x, y, t = route[a][1](i)
                    self.bg.append(shapes.Rectangle(x=x, y=y, width=8, height=1, color=(255, 255, 255), batch=self.batch))
                    self.bg[-1].anchor_y = self.bg[-1].height//2
                    self.bg[-1].anchor_x = self.bg[-1].width//2
                    self.bg[-1].rotation = t

        # Draws traffic lights
        for trafficLight in self.trafficLights:
            x, y, t = trafficLight[0][1](trafficLight[0][0] - 5)
            self.bg.append(shapes.Rectangle(x=x, y=y, width=5, height=ROAD_WIDTH * 2, color=(255, 255, 255), batch=self.batch))
            self.bg[-1].anchor_y = self.bg[-1].height//2
            self.bg[-1].anchor_x = self.bg[-1].width//2
            self.bg[-1].rotation = t
            self.bg.append(shapes.Circle(x, y, 8.5, color=(255, 255, 255), batch=self.batch))
                
    def on_draw(self):
        # Runs the simulation
        for _ in range(150):
            self.simulation.update()
    
        # Draws everything
        self.drawBackground()
        self.drawCars()
        self.drawTrafficLights()
        self.drawPedestrianNums()
        self.drawDataLabels()
        return True, 0

    def drawBackground(self):
        self.clear()
        # Draws white background
        shapes.Rectangle(x=0, y=0, width=self.width+100, height=self.height+100, color=(222, 252, 229)).draw()
        # Draws road setup
        self.batch.draw() 

    def drawCars(self):
        # Loops through cars and draws them
        for car in self.simulation.carManager.cars: 
            car.car.draw()

    def drawTrafficLights(self):
        # Draws traffic light colour
        for trafficLight in self.trafficLights: 
            x, y, t = trafficLight[0][1](trafficLight[0][0]-5)
            shapes.Circle(x, y, 7, color=TRAFFIC_LIGHT_COLOURS[trafficLight[1]]).draw()
        
    def drawPedestrianNums(self):
        # Draws the number of pedestrians waiting at each traffic light
        positioning = [[-45, -10], [25, -10], [-10, 25], [-10, -45]]
        for i, pedestrianNum in enumerate(self.simulation.pedestrianManager.pedestrianNums):
            x, y, t = self.trafficLights[i][0][1](self.trafficLights[i][0][0] - 5)
            x = x + positioning[i][0] + 10
            y = y + positioning[i][1] + 12

            shapes.Circle(x, y, 13, color=(0,0,0)).draw()
            shapes.Circle(x, y, 11, color=(255,255,255)).draw()

            pyglet.text.Label(str(pedestrianNum),
                color=(0, 0, 0, 255),
                font_size=12,
                x=x - 1, y=y + 2,
                anchor_x='center', anchor_y='center').draw()
        
    def drawDataLabels(self):
        # Draws the key for the pedestrian count
        shapes.Circle(350, 92, 8, color=(0,0,0)).draw()
        shapes.Circle(350, 92, 6, color=(255,255,255)).draw()
        pyglet.text.Label(f" - Pedestrian Count",
            color=(0, 0, 0, 255),
            font_size=12,
            x=495, y=95,
            anchor_x='right', anchor_y='center').draw()
                
        labels = [[7, "Average Waiting Time: ", self.simulation.waitingTimeData, "s"],
            [33, "CO2 Emissions (Idle):  ", self.simulation.co2, "g"],
            [59, "Energy Wasted (Idle): ", self.simulation.energyWasted, "J"]]

        # Draws the data labels
        for label in labels:
            pyglet.text.Label(f"{label[1]}{label[2]}{label[3]}",
                color=(0, 0, 0, 255),
                font_size=12,
                x=495, y=label[0],
                anchor_x='right', anchor_y='bottom').draw()
        
# Defines constants
ROAD_WIDTH = 18
CAR_WIDTH = 30
CAR_HEIGHT = 17
ROAD_COLOUR = (82, 90, 96)
TRAFFIC_LIGHT_COLOURS = [(75, 139, 59), (255, 255, 0),  (217, 33, 33)] # Green Yellow Red

# Creates different sections of the road 
# A section is a function which given how far along the section (distance along it travelled) a car is, will return the x, y and angle values
sections = []
sections.append(list(getVerticalData(240, -32, 170))) # bottom 0
sections.append(list(getVerticalData(240, 350, 580))) # Top left 1 
sections.append(list(getVerticalData(300, 580, 360))) # Top right 2 
sections.append(list(getVerticalData(240, 170, 350))) # Middle 3

sections.append(list(getHorizontalData(250, 160, -32))) # left bottom 4
sections.append(list(getHorizontalData(300, -32, 180))) # left top 5
sections.append(list(getHorizontalData(250, 580, 360))) # right bottom 6
sections.append(list(getHorizontalData(300, 420, 580))) # right top 7
sections.append(list(getHorizontalData(300, 180, 420))) # middle top 8
sections.append(list(getHorizontalData(250, 360, 160))) # middle bottom 9

sections.append(list(getEllipseData(240, 170, 160, 250, 1, 1))) # bottom to left 10
sections.append(list(getEllipseData(240, 170, 420, 300, -1, 1))) # bottom to right 11
sections.append(list(getEllipseData(300, 360, 160, 250, 1, -1))) # top to left 12 
sections.append(list(getEllipseData(300, 360, 420, 300, -1, -1))) # top to right 13
sections.append(list(getEllipseData(360, 250, 240, 350, -1, -1))) # right to top 14
sections.append(list(getEllipseData(180, 300, 240, 350, 1, -1))) # left to top 15

# Compiles the sections into a number of different paths a vehicle can take
routes = []
routes.append([sections[0], sections[3], sections[1]]) # bottom up
routes.append([sections[0], sections[10], sections[4]]) # bottom left
routes.append([sections[0], sections[11], sections[7]]) # bottom right

routes.append([sections[2], sections[12], sections[4]]) # top left
routes.append([sections[2], sections[13], sections[7]]) # top right

routes.append([sections[5], sections[8], sections[7]]) # left right
routes.append([sections[5], sections[15], sections[1]]) # left up

routes.append([sections[6], sections[9], sections[4]]) # right left
routes.append([sections[6], sections[14], sections[1]]) # right up

# Loads and runs the ai - uncomment for training
def run(config_file):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    p = neat.Population(config)
    
    with open("winner.bin", "rb") as f:
        genome = pickle.load(f)
    net = neat.nn.FeedForwardNetwork.create(genome, config)
    window = Window(net)
    pyglet.app.run()
local_dir = os.path.dirname(__file__)
config_path = os.path.join(local_dir, 'config.txt')
run(config_path)

# window = Window(1) # Uncomment for RoundRobin
# pyglet.app.run()