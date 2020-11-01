import copy
import random


class Deck(object):

  def __init__(self, cards):
    self.deck = cards
    self.active_deck = []
    self.discard_deck = []
    self.trash_deck = []
    self.shuffle()

  def shuffle(self):
    self.discard_deck = []
    self.active_deck = copy.copy(self.deck)
    random.shuffle(self.active_deck)

  def draw(self, n=1):
    result = []
    for i in xrange(n):
      if not len(self.active_deck):
        self.shuffle()
      c = self.active_deck.pop()
      result += [c]
    return result

  def discard(self, card):
    self.discard_deck.append(card)

  def trash(self, card):
    for i in xrange(len(self.deck)):
      c = self.deck[i]
      if c.type == card.type and c.id == card.id:
        self.deck = self.deck[:i] + self.deck[i+1:]
        break
    self.trash_deck.append(card)

  def put(self, x):
    self.active_deck.append(x)

  def add(self, cards=[]):
    self.deck += cards
    self.shuffle()


class Hand(Deck):
  def __init__(self, cards):
    self.playable_hand = []
    super(Hand, self).__init__(cards)

  def play(self, i):
    if i >= len(self.playable_hand):
      return
    if not self.playable_hand[i]:
      return
    self.playable_hand[i] = None
    all_played = True
    for b in self.playable_hand:
      if b:
        all_played = False
        break
    if all_played:
      self.shuffle()
      self.draw(len(self.playable_hand))
    return

  def trash(self, i):
    if i >= len(self.playable_hand):
      return
    if not self.playable_hand[i]:
      return
    c = self.playable_hand[i]
    self.playable_hand[i] = None
    super(Hand, self).trash(c)

  def draw(self, n=1):
    result = super(Hand, self).draw(n)
    self.playable_hand = result
    return result