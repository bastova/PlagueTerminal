
thread_id = 0


def get_current_thread_id():
  global thread_id
  return thread_id
  

def increment_current_thread_id():
  global thread_id
  thread_id += 1


def set_current_thread_id(id):
  global thread_id
  thread_id = id
