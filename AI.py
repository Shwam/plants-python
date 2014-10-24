#-*-python-*-
from BaseAI import BaseAI
from GameObject import *



class AI(BaseAI):
  """The class implementing gameplay logic."""
  @staticmethod
  def username():
    return "FreakBot"

  @staticmethod
  def password():
    return "password"

  MOTHER, SPAWNER, CHOKER, SOAKER, TUBLEWEED, ARALIA, TITAN, POOL = range(8)
  ##This function is called once, before your first turn
  def init(self):
    pass

  ##This function is called once, after your last turn
  def end(self):
    pass

  def updateCache(self):
    for plant in self.plants:
      plant_pos[(plant.x, plant.y)] = plant

  def spawnable(self):
    spawns = []
    for plant in self.plants:
      if plant.mutation in (MOTHER, SPAWNER):
        for x, y in range(-plant.range, plant.range), range(-plant.range, plant.range):
          spawns.append((plant.x + x, plant.y + y))
    return spawns
    pass

  def forward(self, x, dist):
    if self.playerID:
      return x + dist
    return x - dist

  ##This function is called each time it is your turn
  ##Return true to end your turn, return false to ask the server for updated information
  def run(self):
    cache = self.updateCache()
    if self.players[self.playerID].spores > self.mutations[SPAWNER].spores:
      for plant in self.plants:
        if plant.mutation in (MOTHER, SPAWNER):
          if plant.owner is self.playerID:
            if cache((self.forward(plant.x, 10), plant.y)) is None:
              self.players[self.playerID].germinate(self.forward(plant.x, 10), plant.y, SPAWNER)
              break
    return 1

  def __init__(self, conn):
    BaseAI.__init__(self, conn)
