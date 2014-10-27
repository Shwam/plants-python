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
  enemies = dict()
  enemy_mother = (0,0)
  my_mother = (0, 0)
  closest = (0, 0)
  attackers = (2, 4, 5)
  MOTHER, SPAWNER, CHOKER, SOAKER, TUBLEWEED, ARALIA, TITAN, POOL = range(8)
  ##This function is called once, before your first turn
  def init(self):
    for plant in self.plants:
      if plant.mutation is self.MOTHER:
        if plant.owner is self.playerID:
          self.my_mother = (plant.x, plant.y)
        else:
          self.enemy_mother = (plant.x, plant.y)
    self.closest = self.my_mother
    pass

  ##This function is called once, after your last turn
  def end(self):
    pass

  def updateCache(self):
    self.cache = dict()
    self.mySpawners = dict()
    self.enemies = dict()
    for plant in self.plants:
      self.cache[(plant.x, plant.y)] = plant
      if plant.owner is not self.playerID:
        self.enemies[(plant.x, plant.y)] = plant
      if plant.mutation in (self.MOTHER, self.SPAWNER) and plant.owner is self.playerID:
        self.mySpawners[(plant.x, plant.y)] = plant
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


  def seek(self, target, r):
    closest = self.my_mother
    for x, y in self.mySpawners:
      if self.distance((x, y), target) < self.distance(closest, target):
        closest = (x, y)
    dist = self.distance(closest, target)
    self.closest = closest
    if dist > r:
      print(closest[0] - int(float(r) / dist * (closest[0] - target[0])),closest[1] - int(float(r) / dist * (closest[1] - target[1])) )
      return(closest[0] - int(float(r) / dist * (closest[0] - target[0])),closest[1] - int(float(r) / dist * (closest[1] - target[1])) )
    found = False
    count = 0
    while not found:
      count = count + 1
      for unit in self.radius(target, count):
        if unit not in self.cache and self.distance(closest, unit) < self.mutations[self.SPAWNER].range:
          return unit
    print("ERROR: seek({},{}): Not found???".format(target, r))

  def spawn(self, x, y, mutation):
    if (x, y) not in self.cache:
      self.players[self.playerID].germinate(x, y, mutation)
      return True
    return False

  def spawn_(self):
    target = self.seek(self.enemy_mother, self.mySpawners[self.closest].range)
    if self.distance(self.enemy_mother, self.closest) > self.mutations[self.SPAWNER].range:
      self.spawn(target[0], target[1], self.SPAWNER)
    else:
      self.spawn(target[0], target[1], self.CHOKER)

  def forward(self, x, dist):
    if self.playerID:
      return x + dist
    return x - dist

  def attack(self):
    for plant in self.plants:
      if plant.mutation in self.attackers and plant.owner is self.playerID:
        for enemy in self.enemies:
          if self.distance((plant.x, plant.y), enemy) < plant.range:
            plant.radiate(enemy[0], enemy[1])
    pass

  def run(self):
    self.updateCache()
    self.spawn_()
    self.attack()
    return 1

  def __init__(self, conn):
    BaseAI.__init__(self, conn)