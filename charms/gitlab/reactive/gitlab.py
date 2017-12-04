from charms.reactive import hook
from charmhelpers.core.hookenv import status_set

@hook('config-changed')
def config_changed_handler():
    status_set('active', 'charm installed')
