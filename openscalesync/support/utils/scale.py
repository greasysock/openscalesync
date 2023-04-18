import support.scales.scale as scale
import support.scales.wiifit_scale as wiifit_scale

def load_scale(scale_config) -> scale.Scale:
  if scale_config['adapter'] == 'wiifit':
    return wiifit_scale.WiifitScale(scale_config)

  raise Exception(f"Unknown scale adapter: {scale_config['adapter']}")
