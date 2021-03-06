from firebase import firebase
import threading
import time


_store = None
_commit_timestamp = 0
_lock = threading.Lock()


def _get_store():
  global _store
  if not _store:
    _store = firebase.FirebaseApplication('https://plague-1598856049610.firebaseio.com/', None)
  return _store


def get_commit_timestamp():
  result = _get_store().get('/commit_timestamp', None)
  return int(result)


def put_commit_timestamp():
  global _commit_timestamp
  result = _get_store().put('/', 'commit_timestamp', int(time.time()))
  return result


def should_sync(commit_timestamp):
  global _commit_timestamp
  global _lock
  _lock.acquire()
  result = commit_timestamp > _commit_timestamp
  _commit_timestamp = commit_timestamp
  _lock.release()
  return result


def list_boards():
  result = _get_store().get('/boards', None)
  return [result[k]['id'] for k in result]


def get_board(id):
  result = _get_store().get('/boards', None)
  for k in result:
    if result[k]['id'] == id:
      return k
  return None


def put_board(id):
  result = _get_store().post('/boards', {'id': id, 'started': 0, 'map_tiles': {"1":0, "2":0,"3":0,"4":0,"5":0,"6":0}})
  put_commit_timestamp()
  return result['name']


def get_started(board_name):
  result = _get_store().get('/boards/{}'.format(board_name), None)
  return bool(result['started'])


def set_started(board_name, started=False):
  result = _get_store().patch('/boards/{}'.format(board_name), {'started': int(started)})
  put_commit_timestamp()
  return bool(result['started'])


def list_players(board_name):
  result = _get_store().get('/boards/{}/players'.format(board_name), None)
  return result


def get_player(board_name, id):
  result = _get_store().get('/boards/{}/players'.format(board_name), None)
  for k in result:
    if result[k]['id'] == id:
      return result[k]
  return None


def get_player_by_name(board_name, player_name):
  result = _get_store().get('/boards/{}/players/{}'.format(board_name, player_name), None)
  return result


def put_player(board_name, player):
  result = _get_store().post('/boards/{}/players'.format(board_name), player)
  put_commit_timestamp()
  return result['name']


def set_player(board_name, player_name, player):
  result = _get_store().patch('/boards/{}/players/{}'.format(board_name, player_name), player)
  put_commit_timestamp()
  return player


def move_player(board_name, player_name, tile_id):
  result = _get_store().patch('/boards/{}/players/{}'.format(board_name, player_name), {'map_tile': tile_id})
  put_commit_timestamp()
  return result


def list_cards(board_name):
  result = _get_store().get('/boards/{}/cards'.format(board_name), None)
  if result:
    return result
  return []


def delete_cards(board_name):
  result = _get_store().delete('/boards/{}/cards'.format(board_name), None)
  put_commit_timestamp()
  return result


def put_card(board_name, card):
  result = _get_store().post('/boards/{}/cards'.format(board_name), card)
  put_commit_timestamp()
  return result['name']


def list_map_tiles(board_name):
  result = _get_store().get('/boards/{}/map_tiles'.format(board_name), None)
  return result


def set_plague_to_map(board_name, tile_id, plague):
  result = _get_store().patch('/boards/{}/map_tiles'.format(board_name), {tile_id: plague})
  put_commit_timestamp()
  return result
