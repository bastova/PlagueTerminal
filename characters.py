
class CharacterTypes:
  PEASANT = 'Peasant'
  PRIEST = 'Priest'
  KNIGHT = 'Knight'
  TRADER = 'Trader'

class Character(object):
  def __init__(self, character_type):
    self.gold = 0
    self.plague = 0
    self.character_type = character_type
    self.backstory = ''

  def __repr__(self):
    return 'Type:\n{}\nBackstory:\n{}\n'.format(self.character_type, self.backstory)


class Priest(Character):
  def __init__(self):
    super(Priest, self).__init__(CharacterTypes.PRIEST)
    self.faith = 0
    self.backstory = "The wretched cries of the suffering ring in your ears and haunt your waking dreams. When the first of your brotherhood began to succumb to contagion you cried out to your Lord, beseeching Him for answers. When the people began to die in droves, there was hardly enough time to cover their bodies, let alone give them their last rights. You have held fast your faith, but you are haunted by what you have seen. Now, the great Lady Chance has her hand on the Wheel of Fate, and it threatens to take you along with it. "


class Peasant(Character):
  def __init__(self):
    super(Peasant, self).__init__(CharacterTypes.PEASANT)
    self.productivity = 0
    self.backstory = "Some have said that the contagion entered your little sleepy town as a elderly hag hunched over a broomstick. Whose-ever front steps upon which she swept, were surely to be doomed. Others swear it was two small children holding hands. In the barns and cottages of the places where they slept, the death was sure to follow. You saw the pestilence consume the countryside, and now the lands you once worked lie fallow, and the great House you once owed your loyalty to has been laid low. Where once you saw your life a single continuous life from birth to death in this village, now no longer."


class Knight(Character):
  def __init__(self):
    super(Knight, self).__init__(CharacterTypes.KNIGHT)
    self.authority = 0
    self.backstory = "Generations of your family have served as vassals to King's land. Your father and your father's father and so on for generations have done their rightful duties to the land and to the people who work it. And now you. You watched, mute, as a great wave of death struck your lands, carrying away families, leaving your lands and the surrounding towns with nary but ghosts. You were tucked away in your castle. But you cannot do so for much longer. You sense a change in the winds of fate, the populace (or what remains) stirring, and must answer if you will survive to continue your family's name."


class Trader(Character):
  def __init__(self):
    super(Trader, self).__init__(CharacterTypes.TRADER)
    self.backstory = "It was as if the ship itself was borne aloft by a foetid and rank wind. No sooner had it entered the harbor, when the pestilence - a great, silent wind - began it's foul work in the crowded port city you called home. You saw friends and neighbors struck down, the bustling markets once piled high with the treasures of exotic lands, now piled high with the bodies of the dead. With your remaining family members still living, and the business you built all but decimated, you have retreated."