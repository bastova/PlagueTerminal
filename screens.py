#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import decks
import firebase_connector as store
import main_loop
import master_commands
import numpy
import players
import random
import threading
import threads
import time
import urwid


class ImageWidget(object):
  def __init__(self, image_text, width, height):
    self.image_text = image_text
    self.width = width
    self.height = height

  def image(self):
    return urwid.Text(self.image_text)


def _to_term256_color(r, g, b):
  r = int(round( ( r / 255.0 ) * 5 )) * 36
  g = int(round( ( g / 255.0 ) * 5 )) * 6
  b = int(round( ( b / 255.0 ) * 5 ))
  return r + g + b + 16


def _get_image_text(image):
  width, height = image.size
  image_text = []
  for y in xrange(0, height, 2):
    for x in xrange(width):
      up = image.getpixel((x, y))
      down = image.getpixel((x, y + 1))
      c_up = _to_term256_color(up[0], up[1], up[2])
      c_down = _to_term256_color(down[0], down[1], down[2])
      if x == width - 1:
        char = u'▄\n'
      else:
        char = u'▄'
      image_text.append((urwid.AttrSpec('h%d'%c_down, 'h%d'%c_up, 256), char))
  return (image_text, width, height / 2)


def get_image_widget(image):
  image_text_w_h = _get_image_text(image)
  return ImageWidget(image_text_w_h[0], image_text_w_h[1], image_text_w_h[2])


def get_layered_image_widget(base_image_widget=None, image_widget_pos_list=[], text_pos_list=[]):
  if not base_image_widget:
    return None
  base_image_xy = numpy.reshape(base_image_widget.image_text, (base_image_widget.height, base_image_widget.width, 2))
  for image_widget_pos in image_widget_pos_list:
    image_wt = image_widget_pos[0]
    x = image_widget_pos[2]
    y = image_widget_pos[1]
    image_xy = numpy.reshape(image_wt.image_text, (image_wt.height, image_wt.width, 2))
    if x < 0 or y < 0 or x + image_wt.height >= base_image_widget.height or y + image_wt.width >= base_image_widget.width:
      continue
    for i in xrange(len(image_xy)):
      for j in xrange(len(image_xy[0])):
        base_image_xy[x + i][y + j][0].foreground = image_xy[i][j][0].foreground
        base_image_xy[x + i][y + j][0].background = image_xy[i][j][0].background
  for text_pos in text_pos_list:
    text = text_pos[0]
    x = text_pos[2]
    y = text_pos[1]
    if x < 0 or y < 0 or y + len(text) >= base_image_widget.width or x >= base_image_widget.width:
      continue
    text_l = list(text)
    for i in xrange(len(text_l)):
      base_image_xy[x][y + i][0].foreground = 'white'
      base_image_xy[x][y + i][0].background = 'black'
      base_image_xy[x][y + i][1] = text_l[i]
  result_text = []
  for i in xrange(len(base_image_xy)):
    for j in xrange(len(base_image_xy[0])):
      result_text.append((urwid.AttrSpec(base_image_xy[i][j][0].foreground, base_image_xy[i][j][0].background, 256), base_image_xy[i][j][1]))
  return ImageWidget(result_text, base_image_widget.width, base_image_widget.height)


class BaseScreen(urwid.Pile):
  def __init__(self, statics, screen_wt, screens, widgets):
    self.statics = statics
    self.screen_wt = screen_wt
    self.screens = screens
    self.current_menu_screen_id = 0
    super(BaseScreen, self).__init__(widgets)

  def _start_sync(self):
    threads.increment_current_thread_id()
    self._thread_id = threads.get_current_thread_id()
    self._sync()

  def _stop_sync(self):
    threads.increment_current_thread_id()

  def _build_button(self, text, func):
    button = urwid.Button(text)
    urwid.connect_signal(button, 'click', func, text)
    return button

  def _change_to_menu_screen(self, id, *args):
    if len(self.menu_screens_walker):
      self.menu_screens_walker.pop(0)
    self.current_menu_screen_id = id
    if len(args):
      self.menu_screens_walker.append(self.menu_screens[id](args))
    else:
      self.menu_screens_walker.append(self.menu_screens[id]())

  def _change_to_screen(self, target_screen):
    self.screens.pop(0)
    self.screens.append(target_screen)

  def _sync(self):
    def worker():
      while self._thread_id == threads.get_current_thread_id():
        self.do_sync()
        self.screen_wt.clear()
        main_loop.get_main_loop().draw_screen()
        time.sleep(2)

    t = threading.Thread(target=worker)
    t.start()
    return t

  def do_sync(self):
    pass


class LoginScreen(BaseScreen):
  def __init__(self, statics, screen_wt, screens):
    self.header = get_image_widget(statics.LANDING_IMAGE).image()
    self.menu_screens_walker = urwid.SimpleFocusListWalker([])
    self.menu = urwid.BoxAdapter(urwid.ListBox(self.menu_screens_walker), 10)
    super(LoginScreen, self).__init__(statics, screen_wt, screens, [urwid.Padding(wt) for wt in [self.header, self.menu]])
    self.menu_screens = [self._build_start_screen, self._build_new_board_screen, self._build_connect_to_board_screen]
    self.board_name = ''
    self._change_to_menu_screen(0)

  def _build_start_screen(self):
    body = [urwid.Text("Select board:"), urwid.Divider()]
    for c in [("New board", self._new_board), ("Connect to board", self._connect_to_board)]:
      body.append(urwid.AttrMap(self._build_button(c[0], c[1]), None, focus_map='reversed'))
    return urwid.Pile(body)

  def _build_new_board_screen(self):
    body = [urwid.Text("New Board"), urwid.Divider()]
    for c in [("Ok", self._new_board_ok), ("Back", self._new_board_back)]:
      body.append(urwid.AttrMap(self._build_button(c[0], c[1]), None, focus_map='reversed'))
    input_ = urwid.Edit("> ")
    urwid.connect_signal(input_, 'change', self._on_board_name_change)
    body.append(input_)
    result = urwid.Pile(body)
    result.focus_position = len(result.contents) - 1
    return result

  def _build_connect_to_board_screen(self):
    body = [urwid.Text("Connect to Board"), urwid.Divider()]
    for c in [("Ok", self._connect_to_board_ok), ("Back", self._connect_to_board_back)]:
      body.append(urwid.AttrMap(self._build_button(c[0], c[1]), None, focus_map='reversed'))
    input_ = urwid.Edit("> ")
    urwid.connect_signal(input_, 'change', self._on_board_name_change)
    body.append(input_)
    result = urwid.Pile(body)
    result.focus_position = len(result.contents) - 1
    return result

  def _on_board_name_change(self, edit, new_edit_text):
   self.board_name = new_edit_text

  def _new_board(self, button, choice):
    self._change_to_menu_screen(1)

  def _new_board_ok(self, button, choice):
    if not self.board_name:
      return
    self.statics.BOARD_ID = self.board_name
    self.statics.BOARD_DB_NAME = store.put_board(self.statics.BOARD_ID)
    self.statics.PLAYER_ID = random.randint(0, 100000)
    self.statics.MASTER = True
    self._change_to_screen(CharacterSelectionScreen(self.statics, self.screen_wt, self.screens))

  def _new_board_back(self, button, choice):
    self.board_name = ''
    self._change_to_menu_screen(0)

  def _connect_to_board(self, button, choice):
    self._change_to_menu_screen(2)

  def _connect_to_board_ok(self, button, choice):
    if not self.board_name:
      return
    self.statics.BOARD_ID = self.board_name
    self.statics.BOARD_DB_NAME = store.get_board(self.statics.BOARD_ID)
    if not self.statics.BOARD_DB_NAME:
      return
    self.statics.PLAYER_ID = random.randint(0, 100000)
    self._change_to_screen(CharacterSelectionScreen(self.statics, self.screen_wt, self.screens))

  def _connect_to_board_back(self, button, choice):
    self.board_name = ''
    self._change_to_menu_screen(0)


class CharacterSelectionScreen(BaseScreen):
  def __init__(self, statics, screen_wt, screens):
    self.menu_screens_walker = urwid.SimpleFocusListWalker([])
    self.menu = urwid.BoxAdapter(urwid.ListBox(self.menu_screens_walker), 100)
    super(CharacterSelectionScreen, self).__init__(statics, screen_wt, screens, [urwid.Padding(wt) for wt in [self.menu]])
    self.character_id = 0
    self.image = self.statics.KNIGHT_IMAGE_FULL
    self.menu_screens = [self._build_selection_screen, self._build_character_details_screen, self._build_name_screen]
    self.name = ''
    self._change_to_menu_screen(0)

  def _build_selection_screen(self):
    body = [get_image_widget(self.statics.LANDING_IMAGE).image(), urwid.Text("Pick your character:"), urwid.Divider()]
    for c in [("Knight", self._select_character), ("Priest", self._select_character), ("Peasant", self._select_character), ("Trader", self._select_character)]:
      body.append(urwid.AttrMap(self._build_button(c[0], c[1]), None, focus_map='reversed'))
    return urwid.Pile(body)

  def _build_character_details_screen(self):
    body = [get_image_widget(self.image).image(), urwid.Text("Backstory"), urwid.Divider(), urwid.Text(self.statics.CHARACTERS[self.statics.CHARACTER_ID - 1].backstory), urwid.Divider()]
    for c in [("Ok", self._you_sure_ok), ("Back", self._you_sure_back)]:
      body.append(urwid.AttrMap(self._build_button(c[0], c[1]), None, focus_map='reversed'))
    return urwid.Pile(body)

  def _build_name_screen(self):
    body = [get_image_widget(self.image).image(), urwid.Text("What's your name?"), urwid.Divider()]
    for c in [("Ok", self._name_ok)]:
      body.append(urwid.AttrMap(self._build_button(c[0], c[1]), None, focus_map='reversed'))
    input_ = urwid.Edit("> ")
    urwid.connect_signal(input_, 'change', self._on_name_change)
    body.append(input_)
    result = urwid.Pile(body)
    result.focus_position = len(result.contents) - 1
    return result

  def _on_name_change(self, edit, new_edit_text):
   self.name = new_edit_text

  def _select_character(self, button, choice):
    if choice == 'Knight':
      self.statics.CHARACTER_ID = 1
      self.image = self.statics.KNIGHT_IMAGE_FULL
    elif choice == 'Priest':
      self.statics.CHARACTER_ID = 2
      self.image = self.statics.PRIEST_IMAGE_FULL
    elif choice == 'Peasant':
      self.statics.CHARACTER_ID = 3
      self.image = self.statics.PEASANT_IMAGE_FULL
    elif choice == 'Trader':
      self.statics.CHARACTER_ID = 4
      self.image = self.statics.TRADER_IMAGE_FULL
    self._change_to_menu_screen(1)

  def _you_sure_ok(self, button, choice):
    self._change_to_menu_screen(2)

  def _you_sure_back(self, button, choice):
    self._change_to_menu_screen(0)

  def _name_ok(self, buttin, choice):
    if self.name:
      player = players.Player(self.statics.PLAYER_ID, self.name, self.statics.CHARACTER_ID, 1)
      player.db_name = store.put_player(self.statics.BOARD_DB_NAME, player.to_json_dict())
      self.statics.PLAYERS.append(player)
      self._change_to_screen(LobbyScreen(self.statics, self.screen_wt, self.screens))


class LobbyScreen(BaseScreen):
  def __init__(self, statics, screen_wt, screens):
    self.header = get_image_widget(statics.LANDING_IMAGE).image()
    self.menu_screens_walker = urwid.SimpleFocusListWalker([])
    self.menu = urwid.BoxAdapter(urwid.ListBox(self.menu_screens_walker), 30)
    super(LobbyScreen, self).__init__(statics, screen_wt, screens, [urwid.Padding(wt) for wt in [self.header, self.menu]])
    self.menu_screens = [self._build_players_connected_screen, self._build_you_sure_screen]
    self.connected_players_walker = urwid.SimpleFocusListWalker([])
    self.connected_players_menu = urwid.ListBox(self.connected_players_walker)
    self._change_to_menu_screen(0)
    self._start_sync()

  def _build_players_connected_screen(self):
    body = [urwid.Text("Connected players in {}:".format(self.statics.BOARD_ID)), urwid.Divider(),
        urwid.BoxAdapter(self.connected_players_menu, 20), urwid.Divider()]
    for c in [("Start game", self._start_game)]:
      body.append(urwid.AttrMap(self._build_button(c[0], c[1]), None, focus_map='reversed'))
    return urwid.Pile(body)

  def _build_you_sure_screen(self):
    body = [urwid.Text("Are you sure?"), urwid.Divider()]
    for c in [("Ok", self._you_sure_ok), ("Back", self._you_sure_back)]:
      body.append(urwid.AttrMap(self._build_button(c[0], c[1]), None, focus_map='reversed'))
    return urwid.Pile(body)

  def _start_game(self, button, choice):
    self._change_to_menu_screen(1)

  def _you_sure_ok(self, button, choice):
    self._change_to_screen(GameScreen(self.statics, self.screen_wt, self.screens))

  def _you_sure_back(self, button, choice):
    self._change_to_menu_screen(0)

  def do_sync(self):
    connected_players = store.list_players(self.statics.BOARD_DB_NAME)
    self.statics.PLAYERS = []
    players_list = []
    while len(self.connected_players_walker):
      self.connected_players_walker.pop(0)
    for k in connected_players:
      p = connected_players[k]
      player = players.Player(p['id'], p['name'], p['character'], p['map_tile'])
      player.gold = p['gold']
      player.points = p['points']
      player.plague = p['plague']
      player.db_name = k
      self.statics.PLAYERS.append(player)
      players_list.append(urwid.Text("Player {} connected".format(player.name)))
    self.connected_players_walker.extend(players_list + [urwid.Divider()])
    if store.get_started(self.statics.BOARD_DB_NAME):
      self.statics.STARTED = True


class GameScreen(BaseScreen):
  def __init__(self, statics, screen_wt, screens):
    self.menu_screens_walker = urwid.SimpleFocusListWalker([])
    self.menu = urwid.BoxAdapter(urwid.ListBox(self.menu_screens_walker), 100)
    super(GameScreen, self).__init__(statics, screen_wt, screens, [urwid.Padding(wt) for wt in [self.menu]])
    self.menu_screens = [self._build_game_screen, self._build_hand_screen, self._build_map_screen]
    self.deck = decks.Deck(self.statics.EVENT_CARDS + self.statics.EVENT_CARDS + self.statics.PLAGUE_CARDS + self.statics.TRIUMPH_CARDS)
    self.drawn_cards_walker = urwid.SimpleFocusListWalker([])
    self.drawn_cards_menu = urwid.ListBox(self.drawn_cards_walker)
    self.map_walker = urwid.SimpleFocusListWalker([])
    self.map_menu = urwid.ListBox(self.map_walker)
    self.drawn_cards = []
    if self.statics.CHARACTER_ID == 1:
      hand_ids = [8, 9, 10, 11, 12]
      upgraded_ids = [13, 14, 15]
    elif self.statics.CHARACTER_ID == 2:
      hand_ids = [0, 1, 2, 3, 4]
      upgraded_ids = [5, 6, 7]
    elif self.statics.CHARACTER_ID == 3:
      hand_ids = [16, 17, 18, 19, 20]
      upgraded_ids = [21, 22, 23]
    elif self.statics.CHARACTER_ID == 4:
      hand_ids = [25, 26, 27, 28, 29]
      upgraded_ids = [30, 31, 32]
    hand = []
    for id in hand_ids:
      hand.append(self.statics.CHARACTER_CARDS[id])
    for id in upgraded_ids:
      self.statics.UPGRADED_CARDS.append(self.statics.CHARACTER_CARDS[id])
    self.statics.HAND = decks.Hand(hand)
    self.statics.HAND.draw(5)
    self._change_to_menu_screen(0)
    self._start_sync()

  def _build_game_screen(self):
    player_columns = []
    for player in self.statics.PLAYERS:
      image = self.statics.KNIGHT_IMAGE
      if player.character_id == 1:
        image = self.statics.KNIGHT_IMAGE
      elif player.character_id == 2:
        image = self.statics.PRIEST_IMAGE
      elif player.character_id == 3:
        image = self.statics.PEASANT_IMAGE
      elif player.character_id == 4:
        image = self.statics.TRADER_IMAGE
      player_columns.append(get_image_widget(image).image())
      player_columns.append(urwid.Pile([urwid.Text('{}'.format(player.name)),
          urwid.Text('Gold: {}'.format(player.gold)),
          urwid.Text('Points: {}'.format(player.points)),
          urwid.Text('Plague: {}'.format(player.plague)),
          urwid.Text('Map tile: {}'.format(player.map_tile))]))
    body = [urwid.Columns(player_columns), urwid.Divider(), urwid.BoxAdapter(self.drawn_cards_menu, 20), urwid.Divider(), urwid.Text("Commands:"), urwid.Divider()]
    for c in [("Look at hand", self._look_at_hand),
        ("Look at map", self._look_at_map),
        ("Add to hand", self._add_to_hand),
        ("Hold", self._hold)]:
      body.append(urwid.AttrMap(self._build_button(c[0], c[1]), None, focus_map='reversed'))
    if self.statics.MASTER:
      for c in [("Draw cards", self._draw_cards),
          ("Discard card", self._discard_card),
          ("Trash card", self._trash_card),
          ("Add gold", self._add_gold),
          ("Add points", self._add_points),
          ("Add plague", self._add_plague)]:
        body.append(urwid.AttrMap(self._build_button(c[0], c[1]), None, focus_map='reversed'))
      body.append(urwid.Edit("> "))
    return urwid.Pile(body)

  def _build_hand_screen(self):
    hand_items = []
    if self.statics.HAND:
      for i in xrange(len(self.statics.HAND.playable_hand)):
        card = self.statics.HAND.playable_hand[i]
        hand_items.append(get_image_widget(self.statics.CHARACTER_IMAGE).image())
    hand_pile = urwid.Pile(hand_items)
    
    hold_items = []
    for card in self.statics.HOLD:
      hold_items.append(get_image_widget(self.statics.EVENT_IMAGE).image())
    hold_pile = urwid.Pile(hold_items)
    
    body = [urwid.Columns([hand_pile, hold_pile]), urwid.Text("Commands:"), urwid.Divider()] 
    for c in [("Back", self._hand_back)]:
      body.append(urwid.AttrMap(self._build_button(c[0], c[1]), None, focus_map='reversed'))
    return urwid.Pile(body)

  def _build_map_screen(self):
    body = [urwid.BoxAdapter(self.map_menu, 42), urwid.Divider(), urwid.Text("Move to:"), urwid.Divider()]
    for c in [("Church", self._map_move), ("Harbour", self._map_move), ("Castle", self._map_move),
        ("Market", self._map_move), ("Village", self._map_move), ("Farm", self._map_move)]:
      body.append(urwid.AttrMap(self._build_button(c[0], c[1]), None, focus_map='reversed'))
    body.extend([urwid.Divider(), urwid.AttrMap(self._build_button("Back", self._map_back), None, focus_map='reversed')])
    return urwid.Pile(body)

  def _look_at_hand(self, button, choice):
    self._change_to_menu_screen(1)

  def _look_at_map(self, button, choice):
    self._change_to_menu_screen(2)
  
  def _add_to_hand(self, button, choice):
    pass

  def _hold(self, button, choice):
    pass

  def _hand_back(self, button, choice):
    self._change_to_menu_screen(0)

  def _map_move(self, button, choice):
    id = 1
    if choice == 'Church':
      id = 1
    elif choice == 'Harbour':
      id = 2
    elif choice == 'Castle':
      id = 3
    elif choice == 'Market':
      id = 4
    elif choice == 'Village':
      id = 5
    elif choice == 'Farm':
      id = 6
    store.move_player(self.statics.BOARD_DB_NAME, self.statics.PLAYERS[0].db_name, id)

  def _map_back(self, button, choice):
    self._change_to_menu_screen(0)

  def _draw_cards(self, button, choice):
    master_commands.draw_cards(self.statics, 2, self)

  def _discard_card(self, button, choice):
    pass

  def _trash_card(self, button, choice):
    pass

  def _add_gold(self, button, choice):
    pass

  def _add_points(self, button, choice):
    pass

  def _add_plague(self, button, choice):
    pass

  def do_sync(self):
    connected_players = store.list_players(self.statics.BOARD_DB_NAME)
    self.statics.PLAYERS = []
    while len(self.map_walker):
      self.map_walker.pop(0)
    for k in connected_players:
      p = connected_players[k]
      player = players.Player(p['id'], p['name'], p['character'], p['map_tile'])
      player.gold = p['gold']
      player.points = p['points']
      player.plague = p['plague']
      player.db_name = k
      self.statics.PLAYERS.append(player)
    player_image_widget_pos_list = []
    for player in self.statics.PLAYERS:
      image_token = self.statics.KNIGHT_IMAGE_TOKEN
      x = 0
      y = 0
      if player.character_id == 1:
        image_token = self.statics.KNIGHT_IMAGE_TOKEN
        x = -12
        y = -6
        player_image_widget_pos_list.append((get_image_widget(self.statics.KNIGHT_IMAGE_TOKEN), 4, 4))
      elif player.character_id == 2:
        image_token = self.statics.PRIEST_IMAGE_TOKEN
        y = -6
        player_image_widget_pos_list.append((get_image_widget(self.statics.PRIEST_IMAGE_TOKEN), 16, 4))
      elif player.character_id == 3:
        image_token = self.statics.PEASANT_IMAGE_TOKEN
        x = -12
        player_image_widget_pos_list.append((get_image_widget(self.statics.PEASANT_IMAGE_TOKEN), 4, 10))
      elif player.character_id == 4:
        image_token = self.statics.TRADER_IMAGE_TOKEN
        player_image_widget_pos_list.append((get_image_widget(self.statics.TRADER_IMAGE_TOKEN), 16, 10))
      center_x = 0
      center_y = 0
      if player.map_tile == 1:
        center_x = 17
        center_y = 10
      elif player.map_tile == 2:
        center_x = 52
        center_y = 10
      elif player.map_tile == 3:
        center_x = 84
        center_y = 10
      elif player.map_tile == 4:
        center_x = 17
        center_y = 30
      elif player.map_tile == 5:
        center_x = 52
        center_y = 30
      elif player.map_tile == 6:
        center_x = 84
        center_y = 30
      player_image_widget_pos_list.append((get_image_widget(image_token), center_x + x, center_y + y))
    map_ = get_layered_image_widget(get_image_widget(self.statics.MAP_IMAGE),
      image_widget_pos_list=player_image_widget_pos_list,
      text_pos_list=[(' Church ', 10, 19), (' Harbour ', 44, 19), (' Castle ', 77, 19),
          (' Market ', 10, 38), (' Village ', 44, 38), (' Farm ', 77, 38)]).image()
    self.map_walker.append(map_)

    drawn_cards = store.list_cards(self.statics.BOARD_DB_NAME)
    self.drawn_cards = []
    while len(self.drawn_cards_walker):
      self.drawn_cards_walker.pop(0)
    for k in drawn_cards:
      drawn_card = drawn_cards[k]
      if drawn_card['type'] == 'event':
        card = self.statics.EVENT_CARDS[int(drawn_card['id'])]
        self.drawn_cards.append(card)
        image = self.statics.EVENT_IMAGE
        text = "{}\n{}\n{}".format(card.name, card.description, card.effect)
      elif drawn_card['type'] == 'plague':
        card = self.statics.PLAGUE_CARDS[int(drawn_card['id'])]
        self.drawn_cards.append(card)
        image = self.statics.PLAGUE_IMAGE
        text = "{}\n{}\n{}".format(card.name, card.description, card.effect)
      elif drawn_card['type'] == 'triumph':
        card = self.statics.TRIUMPH_CARDS[int(drawn_card['id'])]
        self.drawn_cards.append(card)
        image = self.statics.EVENT_IMAGE
        text = "{}\n{}\n{}\n{}".format(card.name, card.description, card.effect, card.cost)
      self.drawn_cards_walker.append(urwid.Columns([get_image_widget(image).image(), urwid.Text(text)]))

