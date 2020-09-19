#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import cards
import characters
import main_loop
from PIL import Image
import screens
import sheets_connector
import threads
import time
import urwid
import urwid.raw_display


class Statics(object):
  def __init__(self):
    self.LOG = ''

    self.WIDTH = None
    self.HEIGHT = None

    self.KNIGHT_IMAGE = None
    self.KNIGHT_IMAGE_FULL = None
    self.KNIGHT_IMAGE_TOKEN = None

    self.PRIEST_IMAGE = None
    self.PRIEST_IMAGE_FULL = None
    self.PRIEST_IMAGE_TOKEN = None

    self.PEASANT_IMAGE = None
    self.PEASANT_IMAGE_FULL = None
    self.PEASANT_IMAGE_TOKEN = None

    self.TRADER_IMAGE = None
    self.TRADER_IMAGE_FULL = None
    self.TRADER_IMAGE_TOKEN = None

    self.EVENT_IMAGE = None
    self.CHARACTER_IMAGE = None
    self.PLAGUE_IMAGE = None
    self.MAP_IMAGE = None
    self.LANDING_IMAGE = None

    self.EVENT_CARDS = []
    self.PLAGUE_CARDS = []
    self.CHARACTER_CARDS = []
    self.TRIUMPH_CARDS = []

    self.BOARD_ID = None
    self.BOARD_DB_NAME = None
    self.PLAYER_ID = None
    self.CHARACTER_ID = 1
    self.CHARACTERS = [characters.Knight(), characters.Priest(), characters.Peasant(), characters.Trader()]
    self.MAP_PLAGUE = [0, 0, 0, 0, 0, 0]
    self.PLAYERS = []
    self.PLAYER_TURN = 0
    self.HAND = None
    self.HOLD = []
    self.UPGRADED_CARDS = []
    self.STARTED = False
    self.MASTER = False

    self.KNIGHT_ANIM_FRAMES = []
    self.PRIEST_ANIM_FRAMES = []
    self.TRADER_ANIM_FRAMES = []
    self.PEASANT_ANIM_FRAMES = []


def get_image(image_path):
    image = Image.open(image_path, "r")
    width, height = image.size
    pixel_values = list(image.getdata())
    if image.mode == "RGB":
        channels = 3
    elif image.mode == "RGBA":
        channels = 3 # Ignore the alpha channel
    elif image.mode == "L":
        channels = 1
    else:
        print("Unknown mode: %s" % image.mode)
        return None
    return image


def load_images(statics):
  statics.KNIGHT_IMAGE = get_image('images/knight2.png')
  statics.PRIEST_IMAGE = get_image('images/priest2.png')
  statics.PEASANT_IMAGE = get_image('images/peasant2.png')
  statics.TRADER_IMAGE = get_image('images/trader2.png')

  statics.KNIGHT_IMAGE_FULL = get_image('images/knight5.png')
  statics.PRIEST_IMAGE_FULL = get_image('images/priest5.png')
  statics.PEASANT_IMAGE_FULL = get_image('images/peasant5.png')
  statics.TRADER_IMAGE_FULL = get_image('images/trader5.png')

  statics.KNIGHT_IMAGE_TOKEN = get_image('images/knight0.png')
  statics.PRIEST_IMAGE_TOKEN = get_image('images/priest0.png')
  statics.PEASANT_IMAGE_TOKEN = get_image('images/peasant0.png')
  statics.TRADER_IMAGE_TOKEN = get_image('images/trader0.png')

  statics.EVENT_IMAGE = get_image('images/event1.png')
  statics.CHARACTER_IMAGE = get_image('images/character1.png')
  statics.PLAGUE_IMAGE = get_image('images/plague1.png')
  statics.MAP_IMAGE = get_image('images/map.png')
  statics.LANDING_IMAGE = get_image('images/landing.png')


def load_cards(statics):
  event_cards_values_range = sheets_connector.get_range(sheets_connector.EVENTS_SHEET_NAME, 2, 25, 0, 4)
  for i in range(len(event_cards_values_range)):
    statics.EVENT_CARDS.append(cards.create_event_card(i, event_cards_values_range[i]))
  plague_cards_values_range = sheets_connector.get_range(sheets_connector.PLAGUE_SHEET_NAME, 2, 11, 0, 1)
  for i in range(len(plague_cards_values_range)):
    statics.PLAGUE_CARDS.append(cards.create_plague_card(i, plague_cards_values_range[i]))
  character_cards_values_range = sheets_connector.get_range(sheets_connector.CHARACTERS_SHEET_NAME, 2, 35, 0, 7)
  for i in range(len(character_cards_values_range)):
    statics.CHARACTER_CARDS.append(cards.create_character_card(character_cards_values_range[i]))
  triumph_cards_values_range = sheets_connector.get_range(sheets_connector.TRIUMPHS_SHEET_NAME, 2, 11, 0, 5)
  for i in range(len(triumph_cards_values_range)):
    statics.TRIUMPH_CARDS.append(cards.create_triumph_card(triumph_cards_values_range[i]))


def load_animation(statics):
  for i in xrange(21):
    statics.KNIGHT_ANIM_FRAMES.append(get_image('knight_anim/frames/k{}.png'.format(i)))
    statics.PRIEST_ANIM_FRAMES.append(get_image('priest_anim/frames/{}.png'.format(i)))
    statics.TRADER_ANIM_FRAMES.append(get_image('trader_anim/frames/{}.png'.format(i)))
    statics.PEASANT_ANIM_FRAMES.append(get_image('peasant_anim/frames/{}.png'.format(i)))


def load_resources(statics):
  load_images(statics)
  load_cards(statics)
  load_animation(statics)


def key_presses(key):
  if key in ('q', 'Q'):
    exit_program(button=None)


def exit_program(button):
  threads.increment_all_thread_ids()
  # Let all background sync threads die
  time.sleep(2)
  raise urwid.ExitMainLoop()


def main():
  screen_wt = urwid.raw_display.Screen()
  screen_wt.set_terminal_properties(256)
  screen_wt.reset_default_terminal_palette()

  statics = Statics()
  load_resources(statics)

  screens_walker = urwid.SimpleFocusListWalker([])
  top = urwid.ListBox(screens_walker)
  login_screen = screens.LoginScreen(statics, screen_wt, screens_walker)
  screens_walker.append(login_screen)

  main_loop.set_main_loop(urwid.MainLoop(top, screen=screen_wt, palette=[('reversed', 'standout', '')], unhandled_input=key_presses))
  main_loop.get_main_loop().run()


if __name__ == "__main__":
    main()