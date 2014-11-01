#-*-python-*-
from BaseAI import BaseAI
from GameObject import *
from math import sqrt
import random

class AI(BaseAI):
  """The class implementing gameplay logic."""
  @staticmethod
  def username():
    return "FreakBot"

  @staticmethod
  def password():
    return "password"

  cache = dict()
  mySpawners = dict()
  spawning = dict()
  enemies = dict() 
  health = dict()
  pools = dict()

  my_spores = 0
  enemy_mother = (0,0)
  my_mother = (0, 0)
  attackers = (2, 5)
  branches = [];

  MOTHER, SPAWNER, CHOKER, SOAKER, TUMBLEWEED, ARALIA, TITAN, POOL = range(8)
  ##This function is called once, before your first turn
  def init(self):
    for plant in self.plants:
      if plant.mutation is self.MOTHER:
        if plant.owner is self.playerID:
          self.my_mother = (plant.x, plant.y)
        else:
          self.enemy_mother = (plant.x, plant.y)
    self.branches.append([self.my_mother])
    pass

  ##This function is called once, after your last turn
  def end(self):
    print self.branches
    pass

  def updateCache(self):
    self.cache = dict()
    self.mySpawners = dict()
    self.enemies = dict()
    for h in self.health:
      h = 0
    for plant in self.plants:
      if plant.mutation is not self.POOL:
        self.health[(plant.x, plant.y)] = plant.maxRads - plant.rads
        self.cache[(plant.x, plant.y)] = plant
        if plant.owner is not self.playerID:
          self.enemies[(plant.x, plant.y)] = plant
        elif plant.mutation in (self.MOTHER, self.SPAWNER):
          self.mySpawners[(plant.x, plant.y)] = plant
    for spawn in self.spawning:
      if spawn in self.cache:
        self.spawning[spawn] = 0
    return self.cache

  def distance(self, tuple1, tuple2):
    return int(sqrt(pow(tuple1[0] - tuple2[0], 2) + pow(tuple1[1] - tuple2[1], 2)));
    #return abs(tuple2[0] - tuple1[0]) + abs(tuple2[1] - tuple1[1])

  def radius(self, t, r):
    tiles = []
    for x in range(1-r, r):
      for y in range(1-r, r):
        if x is -r + 1 or x is r -1 or y is -r + 1 or y is r - 1:
          if t[0] + x >= 0 and t[0] - x < self.mapWidth and t[1] + y > 0 and t[1] + y < self.mapHeight: 
            tiles.append((t[0] + x, t[1] + y))
    return tiles

  def find_closest_enemy(self, my_unit):
    closest = self.enemy_mother
    for enemy in self.enemies:
      if self.distance(my_unit, enemy) < self.distance(my_unit, closest):
        closest = enemy
    return closest

  def getClosest(self, target, r):
    closest = self.my_mother
    for x, y in self.mySpawners:
      if self.distance((x, y), target) < self.distance(closest, target):
        closest = (x, y)
    return closest
  
  def checkIntegrity(self, branch):
    #TODO: Check the integrity of the branch and fix if necessary
    pass

  def getTarget(self, head):
    #Determine which branch the head is in
    branchID = 0
    for branch in self.branches:
      if head in branch:
        break
      branchID = branchID + 1

    #Determine the target
    if branchID%2 is 0: # Target nearest enemy
      return self.find_closest_enemy(head)
    elif branchID%2 is 1: # Go straight for mother
      if (head[0] < self.mapWidth*2/5 and self.playerID is 0) or (head[0] > self.mapWidth*3/5 and self.playerID is 1):
        return (self.mapWidth/2, self.mapHeight*5/6)
      return self.enemy_mother
    elif branchID%3 is 2: # TODO: Defensive / Radpool seek?
      return None

  def spawnPoint(self, spawner, target):
    if target is None:
      print("No target specified")
      return None
    if spawner not in self.cache:
      print("Error: spawnPoint spawner at {} does not exist".format(spawner))
      return None
    r = self.mutations[self.SPAWNER].range
    if spawner is self.my_mother:
      r = self.mutations[self.MOTHER].range
    dist = self.distance(spawner, target)
    sPoint = None
    if dist > r:
      sPoint = (spawner[0] - int(float(r) / dist * (spawner[0] - target[0])),spawner[1] - int(float(r) / dist * (spawner[1] - target[1])) )
    else:
      sPoint = target
    if sPoint is None:
      print("Fatal Error. spawnPoint is None")
    if not self.occupied(sPoint[0], sPoint[1]):
      return sPoint
    for _ in range(self.mutations[self.SPAWNER].range):
      for neighbor in self.radius(sPoint, r):
        if not self.occupied(neighbor[0], neighbor[1]) and self.distance(neighbor, spawner) <= r:
          return neighbor
    print("Critical Error - could not find a spawnPoint in range")
    return None

  def bring_to_front(self, unit):
    for enemy in self.enemies:
      if self.distance(unit, enemy) <= self.mutations[self.cache[unit].mutation].range: #it is in range of enemies already
        return

    #find spawners in range
    nearbySpawners = []
    for spawner in self.mySpawners:
      if self.distance(unit, spawner) < self.mutations[self.SPAWNER].range: #Update this for mother weed
        nearbySpawners.append(spawner)
    #find where it is in the branch
    my_branch = None
    for branch in self.branches:
      for spawner in nearbySpawners:
        if spawner in branch:
          if spawner is branch[len(branch) - 1]:
            print("{} is already at the frontline".format(unit))
            return None
          my_branch = branch;
    if my_branch is None:
      print("No spawners in range of {}".format(unit))
      return None
    #bring the unit closer to the front
    for node in nearbySpawners:
      if node not in self.mySpawners:
        print("Branch Error: node {} does not exist".format(node))
        return None
      if node in nearbySpawners:
        if node is my_branch[len(my_branch) - 1]:
          print("{} is already at the frontline".format(unit))
          return None#self.spawnPoint(my_branch[len(my_branch) - 1], self.find_closest_enemy(unit))
        else:
          coord = self.spawnPoint(spawner, my_branch[len(my_branch) - 1])
          print("{} can move to {}".format(unit, coord))
          return coord
        break
    return None

  def occupied(self, x, y):
    return ((x, y) in self.cache or ((x, y) in self.spawning and self.spawning[(x, y)] is not 0))

  def spawn(self, x, y, mutation):
    if not self.occupied(x, y):
      if self.mutations[mutation].spores <= self.my_spores:
        self.my_spores = self.my_spores - self.mutations[mutation].spores
        self.players[self.playerID].germinate(x, y, mutation)
        self.spawning[(x, y)] = mutation
        return True
    return False
  
  def addSpawner(self, x, y, branch):
    #print("Calling addSpawner at ({}) onto {}".format((x, y), branch))
    if self.spawn(x, y, self.SPAWNER):
      #print("Occupied: x, y in self.cache: {}. x, y in self.spawning: {}. self.spawning[(x, y)]: {}".format((x, y) in self.cache, (x, y) in self.spawning, (x, y) in self.spawning and self.spawning[(x, y)] is not 0))
      branch.append((x, y))
      return True
    return False

  def branch_spawn(self):

    for branch in self.branches:
      #print(self.spawning)
      if not branch:
        print("Branch is empty...")
      else:
        head = branch.pop()
        while head not in self.cache and not (head in self.spawning and self.spawning[head] is not 0):
          print("Error: head not in cache")
          head = branch.pop()
        # Make sure the spawner exists
        if head is None:
          print("Error: Head is None")
        elif head in self.spawning and self.spawning[head] is not 0:
          print("Not spawned yet {}".format(head))
        elif head not in self.cache:
          print("CRITICAL ERROR: spawner at {} does not exist. Removing.".format(head))
        else:
          print("Head: {} {}".format(head, self.cache[head].id))

          # Make sure there is a valid target
          branch.append(head)
          goal = self.getTarget(head)
          target = self.spawnPoint(head, goal)
          if target is None:
            print("Error... no target???")
          
          # Path toward it if it is out of range
          elif self.distance(goal, head) > self.mutations[self.SPAWNER].range:
            if not self.addSpawner(target[0], target[1], branch):
              print("Error adding spawner at {}".format(target))
              spawned = False;
              for i in range(5):
                if spawned:
                  break;
                neighbors = self.radius(target, i + 1)
                for neighbor in neighbors:
                  if self.addSpawner(neighbor[0], neighbor[1], branch):
                    spawned = True;
                    break;
          else:
            self.spawn(target[0], target[1], self.CHOKER)
            for rad in range(3):
              for t in self.radius(head, rad*2):
                self.spawn(t[0], t[1], self.ARALIA)
              for t in self.radius(target, rad*2):
                self.spawn(t[0], t[1], random.choice(self.attackers))
  
  def add_branch(self, x, y):
    if self.spawn(x, y, self.SPAWNER):
      self.branches.append([(x, y)])
      return True
    return False
    pass

  def merge_branches(self):
    for branch in self.branches:
      for branch2 in self.branches:
        if (branch in branch2) and branch is not branch2:
          print ("Merging branch {} into {}".format(branch,branch2))
          self.branches.remove(branch)
          break
    pass

  def forward(self, x, dist):
    if self.playerID:
      return x + dist
    return x - dist

  def attack(self):
    for plant in self.plants:
      if plant.mutation in self.attackers and plant.owner is self.playerID:
        for enemy in self.enemies:
          if plant.radiatesLeft > 0 and self.distance((plant.x, plant.y), enemy) < plant.range:
            if enemy not in self.health:
              plant.radiate(enemy[0], enemy[1])
              self.health[enemy] = enemy.maxRads - enemy.rads
            elif self.health[enemy] > 0:
              plant.radiate(enemy[0], enemy[1])
              self.health[enemy] = self.health[enemy] - plant.strength
              break
        '''for _ in range(plant.maxUproots):
        move_to = self.bring_to_front((plant.x, plant.y))
        if move_to is not None:
          print("UPROOTING TO {}".format(move_to))
          self.cache.pop((plant.x, plant.y), "None")
          plant.uproot(move_to[0], move_to[1])
          self.cache[move_to] = plant;'''
    pass

  def run(self):
    #print(" BRANCHES : {}".format(self.branches))
    self.my_spores = self.players[self.playerID].spores
    self.updateCache()
    self.attack()
    self.branch_spawn()
    if self.turnNumber <= 6:
      b = self.branches[len(self.branches) - 1]
      spawner = b[0]
      if spawner in self.cache:
        target = self.spawnPoint(spawner, (spawner[0], self.mapHeight))
        self.add_branch(target[0], target[1])


    return 1

  def __init__(self, conn):
    BaseAI.__init__(self, conn)