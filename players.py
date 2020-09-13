import json


class Player(object):
  def __init__(self, id, name, character_id, map_tile):
    self.db_name = None
    self.id = id
    self.name = name
    self.character_id = character_id
    self.gold = 0
    self.points = 0
    self.plague = 0
    self.map_tile = map_tile

  def patch(self, cp):
    self.gold = cp['gold']
    self.points = cp['points']
    self.plague = cp['plague']
    self.map_tile = cp['map_tile']

  def to_json_dict(self):
   return {'id': self.id, 'name': self.name,
    'character': self.character_id, 'gold': self.gold,
    'points': self.points, 'plague': self.plague,
    'map_tile': self.map_tile}

  def __repr__(self):
    return self.name
