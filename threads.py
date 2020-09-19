
sync_thread_id = 0
anim_thread_id = 0


def get_sync_thread_id():
  global sync_thread_id
  return sync_thread_id
  

def increment_sync_thread_id():
  global sync_thread_id
  sync_thread_id += 1


def set_sync_thread_id(id):
  global sync_thread_id
  sync_thread_id = id


def get_anim_thread_id():
  global anim_thread_id
  return anim_thread_id
  

def increment_anim_thread_id():
  global anim_thread_id
  anim_thread_id += 1


def set_anim_thread_id(id):
  global anim_thread_id
  anim_thread_id = id


def increment_all_thread_ids():
  increment_sync_thread_id()
  increment_anim_thread_id()
