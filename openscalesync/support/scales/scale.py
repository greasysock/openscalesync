class Scale:
  _lower_limit = 0 # kg, will ignore any mass below this

  def __init__(self, config):
    self._is_measuring = False
    self._measure_callback = None
    self._config = config

  def connect(self):
    pass
  def disconnect(self):
    pass

  def measure(self, callback):
    self._is_measuring = True
    self._measure_callback = callback

    callback(self, self._get_mass())

    self._is_measuring = False
    self._measure_callback = None

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
