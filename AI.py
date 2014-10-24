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
  MOTHER, SPAWNER, CHOKER, SOAKER, TUBLEWEED, ARALIA, TITAN, POOL = range(8)
  ##This function is called once, before your first turn
  def init(self):
    pass

  ##This function is called once, after your last turn
  def end(self):
    pass

  def updateCache(self):
    self.cache = dict()
    for plant in self.plants:
      self.cache[(plant.x, plant.y)] = plant
    return self.cache

  def spawn(self):
    for plant in self.plants:
      if self.players[self.playerID].spores < self.plants[self.SPAWNER].spores:
        break
      if plant.mutation in (self.MOTHER, self.SPAWNER):
        if plant.owner is self.playerID:
          if (self.forward(plant.x, 10), plant.y) not in self.cache:
            if self.players[self.playerID].spores > self.mutations[self.SPAWNER].spores:
              self.players[self.playerID].germinate(self.forward(plant.x, 10), plant.y, self.SPAWNER)

  def forward(self, x, dist):
    if self.playerID:
      return x + dist
    return x - dist

  ##This function is called each time it is your turn
  ##Return true to end your turn, return false to ask the server for updated information
  def run(self):
    self.updateCache()
    self.spawn()
    return 1

  def __init__(self, conn):
    BaseAI.__init__(self, conn)
