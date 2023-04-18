from evdev import InputDevice, list_devices, ecodes
import numpy as np
import support.scales.scale as scale
import time
import dbus

def disconnect_device(mac_address):
    bus = dbus.SystemBus()
    manager = dbus.Interface(bus.get_object("org.bluez", "/"), "org.freedesktop.DBus.ObjectManager")

    objects = manager.GetManagedObjects()
    for path, interfaces in objects.items():
        if "org.bluez.Device1" in interfaces:
            device_properties = interfaces["org.bluez.Device1"]
            if device_properties["Address"] == mac_address:
                device = dbus.Interface(bus.get_object("org.bluez", path), "org.bluez.Device1")
                device.Disconnect()
                return
    print(f"Device not found: {mac_address}")

def filter_outliers(data, threshold=1.5):
    Q1 = np.percentile(data, 25)
    Q3 = np.percentile(data, 75)
    IQR = Q3 - Q1
    lower_bound = Q1 - threshold * IQR
    upper_bound = Q3 + threshold * IQR
    return [x for x in data if lower_bound <= x <= upper_bound]

def median_filter(data, window_size=3):
    filtered_data = []
    pad_size = window_size // 2
    padded_data = [data[0]] * pad_size + data + [data[-1]] * pad_size
    for i in range(pad_size, len(padded_data) - pad_size):
        filtered_data.append(np.median(padded_data[i - pad_size : i + pad_size + 1]))
    return filtered_data


def find_wiifit() -> InputDevice:
  for device in [InputDevice(device) for device in list_devices()]:
      if "Nintendo" in device.name:  # You can also use the Wii Fit board's name if you know it
          return device

class WiifitScale(scale.Scale):
  _lower_limit = 10

  @property
  def connected(self):
    return find_wiifit() is not None

  def disconnect(self):
    disconnect_device(self._config['mac'])

  def _get_mass(self):
    wiifit = find_wiifit()
    if wiifit is None:
      return 0
  
    # We need to read the device and get the best value
    # We will start a loop and read the device until we get a good value
    # We will then return that value

    mass_values = [] # will have values like: [12, 45, 88, 88.1, 86], we will need to find the best value
    sensor = np.array([0, 0, 0, 0])
    time_start = time.time()
    for event in wiifit.read_loop():
      if event.type == ecodes.EV_ABS:
        if event.code == ecodes.ABS_HAT0Y:
            sensor[0] = event.value
        elif event.code == ecodes.ABS_HAT0X:
            sensor[1] = event.value
        elif event.code == ecodes.ABS_HAT1Y:
            sensor[2] = event.value
        elif event.code == ecodes.ABS_HAT1X:
            sensor[3] = event.value
        else:
            continue
        mass = np.sum(sensor) / 100

        if mass > self._lower_limit:
          mass_values.append(mass)
  
      if time.time() - time_start > 5:
        break

    filtered_mass = filter_outliers(mass_values)
    median_filtered_mass = median_filter(filtered_mass)
    return np.mean(median_filtered_mass)