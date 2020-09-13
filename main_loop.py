
_main_loop = None


def get_main_loop():
  global _main_loop
  return _main_loop


def set_main_loop(loop):
  global _main_loop
  _main_loop = loop