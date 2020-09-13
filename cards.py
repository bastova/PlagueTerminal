from pprint import pprint


LINE_DIVIDER = '------------------------------------------------------------'


class CardTypes:
  EVENT = 'event'
  CHARACTER = 'character'
  TRIUMPH = 'triumph'
  PLAGUE = 'plague'


class Card(object):
  def __init__(self, id, name, card_type, effect, description, notes):
    self.id = id
    self.name = name
    self.type = card_type
    self.effect = effect
    self.description = description
    self.notes = notes

  def to_json_dict(self):
    return {'id': self.id, 'type': self.type}

  def __repr__(self):
    return '{6}\nId:\n{0}\nName:\n{1}\nType:\n{2}\nEffect:\n{3}\nDescription:\n{4}\nNotes:\n{5}\n'.format(self.id, self.name, self.type, self.effect, self.description, self.notes, LINE_DIVIDER)


class EventCard(Card):
  def __init__(self, id, name, card_type, effect, description, notes):
    super(EventCard, self).__init__(id, name, card_type, effect, description, notes)


class CharacterCard(Card):
  def __init__(self, id, name, card_type, effect, description, notes, character_type):
    super(CharacterCard, self).__init__(id, name, card_type, effect, description, notes)
    self.character_type = character_type


class TriumphCard(Card):
  def __init__(self, id, name, card_type, effect, description, notes, cost):
    super(TriumphCard, self).__init__(id, name, card_type, effect, description, notes)
    self.cost = cost


class PlagueCard(Card):
  def __init__(self, id, name, card_type, effect, description, notes):
    super(PlagueCard, self).__init__(id, name, card_type, effect, description, notes)


def create_event_card(id, row):
  return EventCard(id, row[0], CardTypes.EVENT, row[2], row[3] if len(row) > 3 else '', row[4] if len(row) > 4 else '')


def create_plague_card(id, row):
  return PlagueCard(id, row[0], CardTypes.PLAGUE, '', '', '')


def create_character_card(row):
  return CharacterCard(row[0], row[2], CardTypes.CHARACTER, row[3], row[5], row[6], row[1])


def create_triumph_card(row):
  return TriumphCard(row[0], row[1], CardTypes.TRIUMPH, row[3], row[4], '', row[2])
