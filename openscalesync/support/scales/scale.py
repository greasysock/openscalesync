class Scale:
  def __init__(self, config):
    self._is_measuring = False
    self._measure_callback = None
    self._config = config

  def connect(self):
    pass

  def disconnect(self):
    pass

  def on_measurement(self, callback):
    self._measure_callback = callback

  def _get_mass(self):
    return 0

  # is_measuring getter
  @property
  def is_measuring(self):
    return self._is_measuring

  # connected getter
  @property
  def connected(self):
    return False
