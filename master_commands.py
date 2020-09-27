import firebase_connector as store

def add_gold(statics, input_):
  try:
    parts = input_.split(',')
    player = statics.PLAYERS[int(parts[0])-1]
    player.gold += int(parts[1])
    store.set_player(statics.BOARD_DB_NAME, player.db_name, player.to_json_dict())
  except:
    pass


def add_points(statics, input_):
  try:
    parts = input_.split(',')
    player = statics.PLAYERS[int(parts[0])-1]
    player.points += int(parts[1])
    store.set_player(statics.BOARD_DB_NAME, player.db_name, player.to_json_dict())
  except:
    pass


def add_plague(statics, input_):
  try:
    parts = input_.split(',')
    player = statics.PLAYERS[int(parts[0])-1]
    player.plague += int(parts[1])
    store.set_player(statics.BOARD_DB_NAME, player.db_name, player.to_json_dict())
  except:
    pass


def add_plague_to_map(statics, input_):
  try:
    parts = input_.split(',')
    map_tile = int(parts[0])
    plague = int(parts[1])
    statics.MAP_PLAGUE[map_tile - 1] += plague
    store.set_plague_to_map(statics.BOARD_DB_NAME, map_tile, statics.MAP_PLAGUE[map_tile - 1])
  except:
    pass


def draw_cards(statics, input_, screen):
  try:
    screen.drawn_cards = screen.deck.draw(int(input_))
    for card in screen.drawn_cards:
      store.put_card(statics.BOARD_DB_NAME, card.to_json_dict())
  except:
    pass


def discard_card(statics, input_, screen):
  try:
    id = int(input_)
    if id <= len(screen.drawn_cards):
      card = screen.drawn_cards[id-1]
      screen.drawn_cards = screen.drawn_cards[:id-1] + screen.drawn_cards[id:]
      screen.deck.discard(card)
      store.delete_cards(statics.BOARD_DB_NAME)
      for card in screen.drawn_cards:
        store.put_card(statics.BOARD_DB_NAME, card.to_json_dict())
  except:
    pass


def put_back_card(statics, input_, screen):
  try:
    id = int(input_)
    card = screen.drawn_cards[id-1]
    screen.drawn_cards = screen.drawn_cards[:id-1] + screen.drawn_cards[id:]
    screen.deck.put(card)
    store.delete_cards(statics.BOARD_DB_NAME)
    for card in screen.drawn_cards:
      store.put_card(statics.BOARD_DB_NAME, card.to_json_dict())
  except:
    pass


def add_cards_to_deck(statics, input_, screen):
  try:
    parts = input_.split(',')
    t = int(parts[0])
    i = int(parts[1])
    if t == 'event':
      screen.deck.add(statics.EVENT_CARDS[i])
    elif t == 'plague':
      screen.deck.add(statics.PLAGUE_CARDS[i])
    elif t == 'triumph':
      screen.deck.add(statics.TRIUMPH_CARDS[i])
  except:
    pass


def shuffle_deck(statics, screen):
  screen.deck.shuffle()


def trash_card(statics, input_, screen):
  try:
    id = int(input_)
    if id <= len(screen.drawn_cards):
      card = screen.drawn_cards[id-1]
      screen.drawn_cards = screen.drawn_cards[:id-1] + screen.drawn_cards[id:]
      screen.deck.trash(card)
      store.delete_cards(statics.BOARD_DB_NAME)
      for card in screen.drawn_cards:
        store.put_card(statics.BOARD_DB_NAME, card.to_json_dict())
  except:
    pass


def _end_turn(statics, store, input_, screen):
  if screen.drawn_cards:
    for card in screen.drawn_cards:
      screen.deck.discard(card)
  screen.drawn_cards = []
  store.delete_cards(statics.BOARD_DB_NAME)
  statics.PLAYER_TURN += 1
  if statics.PLAYER_TURN >= len(statics.PLAYERS):
    statics.PLAYER_TURN = 0

