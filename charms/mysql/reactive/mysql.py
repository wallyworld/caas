from charms.reactive import when, when_not
from charms.reactive import set_flag, clear_flag
from charmhelpers.core.hookenv import (
    log,
    metadata,
    status_set,
    config,
    network_get,
    relation_id,
)


from charms import layer


@when_not('layer.docker-resource.mysql_image.fetched')
def fetch_image():
    layer.docker_resource.fetch('mysql_image')


@when('mysql.configured')
def mysqlb_active():
    status_set('active', '')


@when('layer.docker-resource.mysql_image.available')
@when_not('mysql.configured')
def config_mysql():
    status_set('maintenance', 'Configuring mysql container')

    spec = make_pod_spec()
    log('set pod spec:\n{}'.format(spec))
    layer.caas_base.pod_spec_set(spec)

    set_flag('mysql.configured')


def make_pod_spec():
    with open('reactive/spec_template.yaml') as spec_file:
        pod_spec_template = spec_file.read()

    md = metadata()
    cfg = config()

    user = cfg.get('user')
    password = cfg.get('password')
    database = cfg.get('database')
    root_password = cfg.get('root_password')

    image_info = layer.docker_resource.get_info('mysql_image')

    data = {
        'name': md.get('name'),
        'docker_image_path': image_info.registry_path,
        'docker_image_username': image_info.username,
        'docker_image_password': image_info.password,
        'port': cfg.get('mysql_port'),
        'user': user,
        'password': password,
        'database': database,
        'root_password': root_password,
    }
    data.update(cfg)
    return pod_spec_template % data


@when('mysql.configured')
@when('server.database.requested')
def provide_database(mysql):
    log('db requested')

    info = network_get('server', relation_id())
    log('network info {0}'.format(info))
    host = info.get('ingress-addresses', [""])[0]
    if not host:
        log("no service address yet")
        return

    cfg = config()
    user = cfg.get('user')
    password = cfg.get('password')
    database = cfg.get('database')

    for request, application in mysql.database_requests().items():
        log('request -> {0} for app -> {1}'.format(request, application))

        log('db params: {0}:...@{1}'.format(user, database))

        mysql.provide_database(
            request_id=request,
            host=host,
            port=3306,
            database_name=database,
            user=user,
            password=password,
        )
        clear_flag('server.database.requested')
