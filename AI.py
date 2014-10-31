#-*-python-*-
from BaseAI import BaseAI
from GameObject import *
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
  enemy_mother = (0,0)
  my_mother = (0, 0)
  closest = (0, 0)
  attackers = (2, 4, 5)
  last_spawn = 0;
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
    self.closest = self.my_mother
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
    return abs(tuple2[0] - tuple1[0]) + abs(tuple2[1] - tuple1[1])

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
    #print("Closest Enemy: {}... Enemy Mother: {}".format(closest, self.enemy_mother))
    return closest

  def seek(self, target, r):
    closest = self.my_mother
    for x, y in self.mySpawners:
      if self.distance((x, y), target) < self.distance(closest, target):
        closest = (x, y)
    dist = self.distance(closest, target)
    self.closest = closest
    if dist > r:
      #print(closest[0] - int(float(r) / dist * (closest[0] - target[0])),closest[1] - int(float(r) / dist * (closest[1] - target[1])) )
      return(closest[0] - int(float(r) / dist * (closest[0] - target[0])),closest[1] - int(float(r) / dist * (closest[1] - target[1])) )
    found = False
    count = 0
    for count in range(8):
      for unit in self.radius(target, count):
        if not self.occupied(unit[0], unit[1]) and self.distance(closest, unit) < self.mutations[self.SPAWNER].range:
          return unit
    print("ERROR: seek({},{}): Exceeded Range".format(target, r))

  def occupied(self, x, y):
    return ((x, y) in self.cache or ((x, y) in self.spawning and self.spawning[(x, y)] is 0))

  def spawn(self, x, y, mutation):
    if not self.occupied(x, y):
      self.players[self.playerID].germinate(x, y, mutation)
      self.spawning[(x, y)] = mutation
      return True
    return False
  
  def addSpawner(self, x, y, branch):
    if self.spawn(x, y, self.SPAWNER):
      self.branches[branch].append((x, y))
      return True
    return False

  def branch_spawn(self):

    for branch in self.branches:
      head = branch.pop()

      # Make sure the spawner exists
      if head is None:
        print("Error: Head is None")
        return
      if head in self.spawning and self.spawning[head] is not 0:
        print("Not spawned {}".format(head))
        return
      elif head not in self.cache:
        print("Error: spawner at {} does not exist. Removing.".format(head))
        return
      
      # Make sure there is a valid target
      branch.append(head)
      nearest_enemy = self.find_closest_enemy(head)
      target = self.seek(nearest_enemy, self.mutations[self.MOTHER].range if self.my_mother is self.closest else self.mutations[self.SPAWNER].range)
      if target is None:
        print("Error... no target???")
        return
      
      # Path toward it if it is out of range
      if self.distance(nearest_enemy, head) > self.mutations[self.SPAWNER].range:
        if not self.addSpawner(target[0], target[1], 0):
          print("Error adding spawner at {}".format(target))
          spawned = False;
          for i in range(5):
            if spawned:
              break;
            neighbors = self.radius(target, i + 1)
            for neighbor in neighbors:
              if self.spawn(neighbor[0], neighbor[1], self.SPAWNER):
                spawned = True;
                break;

      else:
        self.spawn(target[0], target[1], self.CHOKER)
        for rad in range(3):
          for t in self.radius(target, rad*2):
            self.spawn(t[0], t[1], random.choice(self.attackers))

      
  
  def add_branch(self):
    pass

  def merge_branches(self):
    for branch in self.branches:
      for branch2 in self.branches:
        if (branch in branch2) and branch is not branch2:
          self.branches.remove(branch)
    pass

  def spawn_(self):
    nearest_enemy = self.find_closest_enemy(self.my_mother)
    target = self.seek(nearest_enemy, self.mutations[self.MOTHER].range if self.my_mother is self.closest else self.mutations[self.SPAWNER].range)
    if self.distance(nearest_enemy, self.closest) > self.mutations[self.SPAWNER].range:
      if not self.addSpawner(target[0], target[1], 0):
        print("COULD NOT SPAWN AT {}".format(target))
        if (self.turnNumber - self.last_spawn > 5):
          spawned = False;
          for i in range(5):
            if spawned is True:
              break;
            neighbors = self.radius(target, i + 1)
            for neighbor in neighbors:
              if self.spawn(neighbor[0], neighbor[1], self.SPAWNER):
                spawned = True;
                break;
            if spawned:
              self.last_spawn = self.turnNumber
      else:
        self.last_spawn = self.turnNumber

    else:
      self.spawn(target[0], target[1], self.CHOKER)
      for rad in range(3):
        for t in self.radius(target, rad*2):
          self.spawn(t[0], t[1], random.choice(self.attackers))

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
              #plant.talk("EXTERMINATE!!!")
              print("EXTERMINATE!!!")
              plant.radiate(enemy[0], enemy[1])
              self.health[enemy] = self.health[enemy] - plant.strength
              break
    pass

  def run(self):
    self.updateCache()
    #if self.turnNumber < 50 or self.playerID is 0:
    self.attack()
    #if self.playerID is 0:
    self.branch_spawn()

    return 1

  def __init__(self, conn):
    BaseAI.__init__(self, conn)