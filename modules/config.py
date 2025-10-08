from configparser import ConfigParser, ExtendedInterpolation

cfg = ConfigParser(interpolation=ExtendedInterpolation(), allow_no_value=True)
cfg.read('./modules/config.cfg')

DEBUGGING = cfg.getboolean('Main', 'debugging')

GUILD = cfg.get('Settings', 'guild')