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

  uprootRange = 50  # SHOULD BE GLOBAL CONSTANT

  cache = dict()
  mySpawners = dict()
  spawning = dict()
  enemies = dict() 
  health = dict()
  pools = dict()
  budget = dict()
  healers = dict()

  my_spores = 0
  enemy_mother = (0,0)
  my_mother = (0, 0)
  attackers = (2, 5)
  branches = []
  mode = 0
  num_turns = 0
  num_plants = 0

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
    print self.num_turns
    pass

  def updateCache(self):
    self.cache = dict()
    self.mySpawners = dict()
    self.spawning = dict()
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
        elif plant.mutation is self.TUMBLEWEED:
          self.healers[(plant.x, plant.y)] = plant
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

  def getBranchID(self, unit):
    branchID = 0
    found = False
    for branch in self.branches:
      if unit in branch:
        found = True
        break
      branchID = branchID + 1
    if found:
      return branchID
    return None

  def branchID(self, branch):
    for i in range(len(self.branches)):
      if branch is self.branches[i]:
        return i
    print("E R R O R : Branch does not exist.")

  def getTarget(self, head):
    #Determine which branch the head is in
    branchID = self.getBranchID(head)

    #Determine the target
    if branchID%2 is 0: # Target nearest enemy
      return self.find_closest_enemy(head)
    elif branchID%2 is 1: # Go straight for mother
      if (head[0] < self.mapWidth*2/5 and self.playerID is 0) or (head[0] > self.mapWidth*3/5 and self.playerID is 1):
        return (self.mapWidth/2, self.mapHeight*5/6)
      return self.enemy_mother
    elif branchID%3 is 2: # Defensive
      target = self.find_closest_enemy(self.my_mother)
      if self.distance(self.my_mother, target) < 800:
        return target
      #If the nearest spawner is closer to the threat than the head of this branch, spawn a new defensive branch instead
      return None

  def movePoint(self, origin, target):
    if target is None or origin not in self.cache:
      return None
    r = self.uprootRange
    if self.cache[origin].mutation is self.TUMBLEWEED:
      r = self.bumbleweedSpeed
    dist = self.distance(origin, target)
    sPoint = None
    if dist > r:
      sPoint = (origin[0] - int(float(r) / dist * (origin[0] - target[0])),origin[1] - int(float(r) / dist * (origin[1] - target[1])) )
    else:
      sPoint = target
    if not self.occupied(sPoint[0], sPoint[1]):
      return sPoint
    for rad in range(15):
      for neighbor in self.radius(sPoint, rad):
        if not self.occupied(neighbor[0], neighbor[1]) and self.distance(neighbor, origin) < r:
          return neighbor
    return None

  def spawnPoint(self, spawner, target):
    if target is None:
      #print("No target specified")
      return None
    if spawner not in self.cache:
      print("Error: spawnPoint spawner at {} does not exist".format(spawner))
      return None
    r = self.cache[spawner].range
    dist = self.distance(spawner, target)
    sPoint = None
    if dist > r:
      sPoint = (spawner[0] - int(float(r) / dist * (spawner[0] - target[0])),spawner[1] - int(float(r) / dist * (spawner[1] - target[1])) )
    else:
      sPoint = target
    if not self.occupied(sPoint[0], sPoint[1]):
      return sPoint
    for rad in range(self.mutations[self.SPAWNER].range):
      for neighbor in self.radius(sPoint, rad):
        if not self.occupied(neighbor[0], neighbor[1]) and self.distance(neighbor, spawner) <= r:
          return neighbor
    print("Critical Error - could not find a spawnPoint in range")
    return None

  def getBranch(self, unit):
    for spawner in self.mySpawners:
      if self.distance(unit, spawner) < self.cache[spawner].range:
        return spawner

  def bring_to_front(self, unit):
    spawner = self.getBranch(unit)
    if spawner is None:
      return None
    #bring the unit closer to the front
    point = self.movePoint(unit, self.find_closest_enemy(unit))
    return point
    
    '''#find spawners in range
    spawner = self.getBranch(unit)
    if spawner is None:
      return None
    #bring the unit closer to the front
    point = self.spawnPoint(spawner, self.getTarget(spawner))
    return point'''

  def occupied(self, x, y):
    return ((x, y) in self.cache or ((x, y) in self.spawning and self.spawning[(x, y)] is not 0))

  def spawn(self, x, y, mutation):
    if not self.occupied(x, y):
      if self.mutations[mutation].spores <= self.my_spores:
        self.my_spores = self.my_spores - self.mutations[mutation].spores
        self.players[self.playerID].germinate(x, y, mutation)
        self.spawning[(x, y)] = mutation
        self.num_plants = self.num_plants + 1
        return True
    return False
  
  def spawnFrom(self, x, y, mutation, branchID):
    if self.budget[branchID] > self.mutations[mutation].spores:
      if self.spawn(x, y, mutation):
        self.budget[branchID] = self.budget[branchID] - self.mutations[mutation].spores
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
          #print("Head: {} {}".format(head, self.cache[head].id))

          # Make sure there is a valid target
          branch.append(head)
          branchID = self.getBranchID(head)

          goal = self.getTarget(head)
          target = self.spawnPoint(head, goal)

          if branchID >= len(self.branches) or target is None:
            self
          # Path toward it if it is out of range
          elif self.distance(goal, head) > self.mutations[self.SPAWNER].range:
            if not self.addSpawner(target[0], target[1], branch):
              #print("Error adding spawner at {}".format(target))
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
            self.spawnFrom(target[0], target[1], self.CHOKER, branchID)
            spawn = self.spawnPoint(head, head)
            self.spawn(spawn[0], spawn[1], self.TUMBLEWEED)
            for rad in range(5):
              for t in self.radius(goal, rad):
                self.spawnFrom(t[0], t[1], random.choice(self.attackers), branchID)
  
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
    if self.playerID is 0:
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
        # UPROOT
        spawned = False
        move_to = self.bring_to_front((plant.x, plant.y))
        if move_to is not None and self.distance((plant.x, plant.y), move_to) >= plant.range:
          for rad in range(5):
            if not spawned:
              for t in self.radius(move_to, rad):
                if not self.occupied(t[0], t[1]) and not spawned:
                  plant.uproot(move_to[0], move_to[1])
                  self.cache[move_to] = plant;
                  spawned = True
        #plant.uproot(self.forward((plant.x), random.randint(40,50)), plant.y)
    pass


  def defend(self):
    for enemy in self.enemies:
      if self.distance(enemy, self.my_mother) < self.mutations[self.MOTHER].range * 2:
        spawn = self.spawnPoint(self.my_mother, enemy)
        self.spawn(spawn[0], spawn[1], self.TITAN)

        for _ in range(8):
          spawn = self.spawnPoint(self.my_mother, enemy)
          self.spawn(spawn[0], spawn[1], self.CHOKER)
  
  def nearest_damaged_unit(self, healer):
    closest = self.my_mother
    for plant in self.plants:
      if plant.owner is self.playerID and plant.rads > 0:
        if self.distance(healer, (plant.x, plant.y)) < self.distance(healer, closest):
          closest = (plant.x, plant.y)
    if self.my_mother is closest:
      return None
    return closest


  def heal(self):
    for healer in self.plants:
      if healer.owner is self.playerID and healer.mutation is self.TUMBLEWEED:
        #healer.uproot(self.forward(healer.x, self.bumbleweedSpeed), healer.y)
        for plant in self.plants:
          if plant.owner is self.playerID and (plant.x, plant.y) in self.health and plant.mutation is not self.MOTHER:
            closest = self.nearest_damaged_unit((healer.x, healer.y))
            if closest is not None:
              if self.distance((healer.x, healer.y), closest) < healer.range:
                healer.radiate(closest[0], closest[1])
                break
              moveTo = self.movePoint((healer.x, healer.y), closest)
              healer.uproot(moveTo[0], moveTo[1])
              break
            #print("Ready to heal {}".format(self.health[(plant.x, plant.y)]))


  def setBudget(self):
    self.budget = dict()
    for i in range(len(self.branches)):
      self.budget[i] = self.my_spores / len(self.branches)

  def run(self):
    self.num_turns = self.num_turns + 1
    self.mode = 0#self.playerID#1 - self.playerID
    self.my_spores = self.players[self.playerID].spores
    self.updateCache()
    self.setBudget()

    if self.mode == 0: #Branch Out strategy
      #print(" BRANCHES : {}".format(self.branches))
      self.defend()
      self.heal()
      self.setBudget()
      self.attack()
      self.branch_spawn()
      if self.turnNumber <= 3:
        b = self.branches[len(self.branches) - 1]
        spawner = b[0]
        if spawner in self.cache:
          target = self.spawnPoint(spawner, (spawner[0], self.mapHeight))
          if target is not None:
            self.add_branch(target[0], target[1])


    if self.mode == 1: #Cluster-Defense Strategy
      for plant in self.plants:
        if plant.owner is self.playerID and plant.mutation is not self.MOTHER:
          plant.uproot(self.forward((plant.x), random.randint(40, self.uprootRange)), plant.y)
      while self.num_plants < self.maxPlants and self.my_spores >= self.mutations[self.ARALIA].spores:
        self.spawn(self.my_mother[0] + random.randint(-150, 150), self.my_mother[1] + random.randint(-150, 150), self.ARALIA)
      self.attack()

    #print("{} -> {}".format(self.players[self.playerID].spores, self.my_spores))
    return 1

  def __init__(self, conn):
    BaseAI.__init__(self, conn)