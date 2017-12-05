from charms.layer.hookenv import container_spec_set
from charms.reactive import when_not, set_state
from charmhelpers.core.hookenv import log, metadata, status_set, config

from string import Template

@when_not('gitlab.configured')
def config_gitlab():
    status_set('maintenance', 'Configuring Gitlab')

    spec = make_pod_spec()
    log('set container spec:\n{}'.format(spec))
    container_spec_set(spec)

    set_state('gitlab.configured')
    status_set('active', 'gitlab configured')

def make_pod_spec():
    pod_spec_file = open('reactive/node_template.yaml')
    pod_spec_template = Template(pod_spec_file.read())

    cfg = config()
    d = {
        'image': cfg.get('image'),
        'port': cfg.get('port'),
    }
    md = metadata()
    d = {
        'name': md.get('name'),
        'image': 'gitlab/gitlab-ce:9.5.2-ce.0',
        'port': 80,
    }
    return pod_spec_template.substitute(d)
