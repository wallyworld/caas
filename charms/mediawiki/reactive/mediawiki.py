from charms.reactive import when, when_not, hook
from charms.reactive import endpoint_from_flag
from charms.reactive.flags import set_flag, get_state, clear_flag
from charmhelpers.core.hookenv import (
    log,
    metadata,
    status_set,
    config,
)

from charms import layer


@when_not('layer.docker-resource.mediawiki_image.fetched')
@when('mediawiki.db.related')
def fetch_image():
    layer.docker_resource.fetch('mediawiki_image')


@when_not('mediawiki.db.related')
@when_not('mediawiki.configured')
def mediawiki_blocked():
    status_set('blocked', 'Waiting for database')


@when('mediawiki.db.related')
@when('mediawiki.configured')
def mediawiki_active():
    status_set('active', '')


@hook('upgrade-charm')
def upgrade():
    clear_flag('mediawiki.configured')


@when_not('mediawiki.configured')
@when('mediawiki.db.related')
@when('layer.docker-resource.mediawiki_image.available')
def config_mediawiki():
    dbcfg = get_state('mediawiki.db.config')
    log('got db {0}'.format(dbcfg))

    status_set('maintenance', 'Configuring mediawiki container')

    spec = make_pod_spec(dbcfg)
    log('set pod spec:\n{}'.format(spec))
    layer.caas_base.pod_spec_set(spec)

    set_flag('mediawiki.configured')


@when('db.available')
@when_not('mediawiki.db.related')
def db_changed():
    log('db available')
    set_flag('mediawiki.db.related')


def make_pod_spec(dbcfg):
    image_info = layer.docker_resource.get_info('mediawiki_image')

    with open('reactive/spec_template.yaml') as spec_file:
        pod_spec_template = spec_file.read()

    md = metadata()
    cfg = config()
    mysql = endpoint_from_flag('db.available')
    data = {
        'name': md.get('name'),
        'docker_image_path': image_info.registry_path,
        'docker_image_username': image_info.username,
        'docker_image_password': image_info.password,
        'http_port': cfg.get('http_port'),
        'host': mysql.host(),
        'database': mysql.database(),
        'user': mysql.user(),
        'password': mysql.password(),
    }
    return pod_spec_template % data
