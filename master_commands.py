import firebase_connector as store

def _add_gold(statics, input_):
  parts = input_.split(',')
  player = statics.PLAYERS[int(parts[0])-1]
  player.gold += int(parts[1])
  store.set_player(statics.BOARD_DB_NAME, player.db_name, player.to_json_dict())


def _subtract_gold(statics, store, input_):
  parts = input_.split(',')
  player = statics.PLAYERS[int(parts[0])-1]
  player.gold -= int(parts[1])
  store.set_player(statics.BOARD_DB_NAME, player.db_name, player.to_json_dict())


def _add_points(statics, store, input_):
  parts = input_.split(',')
  player = statics.PLAYERS[int(parts[0])-1]
  player.points += int(parts[1])
  store.set_player(statics.BOARD_DB_NAME, player.db_name, player.to_json_dict())


def _subtract_points(statics, store, input_):
  parts = input_.split(',')
  player = statics.PLAYERS[int(parts[0])-1]
  player.points -= int(parts[1])
  store.set_player(statics.BOARD_DB_NAME, player.db_name, player.to_json_dict())


def _add_plague(statics, store, input_):
  parts = input_.split(',')
  player = statics.PLAYERS[int(parts[0])-1]
  player.plague += int(parts[1])
  store.set_player(statics.BOARD_DB_NAME, player.db_name, player.to_json_dict())


def _subtract_plague(statics, store, input_):
  parts = input_.split(',')
  player = statics.PLAYERS[int(parts[0])-1]
  player.plague -= int(parts[1])
  store.set_player(statics.BOARD_DB_NAME, player.db_name, player.to_json_dict())


def _add_plague_to_map(statics, store, input_):
  parts = input_.split(',')
  map_tile = int(parts[0])
  plague = int(parts[1])
  statics.MAP_PLAGUE[map_tile - 1] += plague
  store.set_plague_to_map(statics.BOARD_DB_NAME, map_tile, statics.MAP_PLAGUE[map_tile - 1])


def _subtract_plague_from_map(statics, store, input_):
  parts = input_.split(',')
  map_tile = int(parts[0])
  plague = int(parts[1])
  statics.MAP_PLAGUE[map_tile - 1] -= plague
  store.set_plague_to_map(statics.BOARD_DB_NAME, map_tile, statics.MAP_PLAGUE[map_tile - 1])


def draw_cards(statics, input_, screen):
  if screen.drawn_cards:
    return
  screen.drawn_cards = screen.deck.draw(int(input_))
  for card in screen.drawn_cards:
    store.put_card(statics.BOARD_DB_NAME, card.to_json_dict())


def _discard_card(statics, store, input_, screen):
  id = int(input_)
  if id <= len(screen.drawn_cards):
    card = screen.drawn_cards[id-1]
    screen.drawn_cards = screen.drawn_cards[:id-1] + screen.drawn_cards[id:]
    screen.deck.discard(card)
    store.delete_cards(statics.BOARD_DB_NAME)
    for card in screen.drawn_cards:
      store.put_card(statics.BOARD_DB_NAME, card.to_json_dict())


def _put_back_card(statics, store, input_, screen):
  id = int(input_)
  card = screen.drawn_cards[id-1]
  screen.drawn_cards = screen.drawn_cards[:id-1] + screen.drawn_cards[id:]
  screen.deck.put(card)
  store.delete_cards(statics.BOARD_DB_NAME)
  for card in screen.drawn_cards:
    store.put_card(statics.BOARD_DB_NAME, card.to_json_dict())


def _add_cards_to_deck(statics, store, input_, screen):
  parts = input_.split(',')
  t = int(parts[0])
  i = int(parts[1])
  if t == 'event':
    screen.deck.add(statics.EVENT_CARDS[i])
  elif t == 'plague':
    screen.deck.add(statics.PLAGUE_CARDS[i])
  elif t == 'triumph':
    screen.deck.add(statics.TRIUMPH_CARDS[i])


def _shuffle_deck(statics, store, input_, screen):
  screen.deck.shuffle()


def _trash_card(statics, store, input_, screen):
  id = int(input_)
  if id <= len(screen.drawn_cards):
    card = screen.drawn_cards[id-1]
    screen.drawn_cards = screen.drawn_cards[:id-1] + screen.drawn_cards[id:]
    screen.deck.trash(card)
    store.delete_cards(statics.BOARD_DB_NAME)
    for card in screen.drawn_cards:
      store.put_card(statics.BOARD_DB_NAME, card.to_json_dict())


def _end_turn(statics, store, input_, screen):
  if screen.drawn_cards:
    for card in screen.drawn_cards:
      screen.deck.discard(card)
  screen.drawn_cards = []
  store.delete_cards(statics.BOARD_DB_NAME)
  statics.PLAYER_TURN += 1
  if statics.PLAYER_TURN >= len(statics.PLAYERS):
    statics.PLAYER_TURN = 0

