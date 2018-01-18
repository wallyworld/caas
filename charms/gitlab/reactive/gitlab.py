from charms.layer.hookenv import container_spec_set
from charms.reactive import when_not, set_state
from charmhelpers.core.hookenv import log, metadata, status_set, config

from string import Template


@when_not('gitlab.configured')
def config_gitlab():
    status_set('maintenance', 'Configuring Gitlab')

    spec = make_container_spec()
    log('set container spec:\n{}'.format(spec))
    container_spec_set(spec)

    set_state('gitlab.configured')
    status_set('active', 'gitlab configured')


def make_container_spec():
    spec_file = open('reactive/spec_template.yaml')
    pod_spec_template = Template(spec_file.read())

    md = metadata()
    cfg = config()
    data = {
        'name': md.get('name'),
        'image': cfg.get('gitlab_image'),
        'port': cfg.get('http_port'),
        'config': compose_config(cfg)
    }
    return pod_spec_template.substitute(data)


def isfloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


def format_config_value(value):
    val = str(value)
    if isinstance(value, bool):
        if value:
            val = "true"
        else:
            val = "false"
    elif val.isdigit():
        val = int(val)
    elif isfloat(val):
        val = float(val)
    else:
        val = "'{}'".format(val)
    return val


def compose_config(cfg):
    exturl = None

    if cfg.get('external_url'):
        exturl = cfg.get('external_url')
        if exturl != '' and not exturl.startswith("http"):
            exturl = "http://" + exturl

    http_port = cfg.get('http_port')
    if exturl is not None and http_port is not None:
        if exturl.endswith("/"):
            exturl = exturl[:-1]

        exturl = exturl + ":{}".format(http_port)

    cfg_terms = []
    if exturl is not None:
        cfg_terms = ['external_url {}'.format(format_config_value(exturl))]

    def maybe_add_config(cfg_terms, k, v):
        if v is None or str(v) == '':
            return
        cfg_terms += ['{}={}'.format(k, format_config_value(v))]

    maybe_add_config(cfg_terms, 'gitlab_rails[\'gitlab_ssh_host\']',
                     cfg.get('ssh_host')),
    maybe_add_config(cfg_terms, 'gitlab_rails[\'time_zone\']',
                     cfg.get('time_zone')),
    maybe_add_config(cfg_terms, 'gitlab_rails[\'gitlab_email_from\']',
                     cfg.get('email_from')),
    maybe_add_config(cfg_terms, 'gitlab_rails[\'gitlab_email_display_name\']',
                     cfg.get('from_email_name')),
    maybe_add_config(cfg_terms, 'gitlab_rails[\'gitlab_email_reply_to\']',
                     cfg.get('reply_to_email')),
    maybe_add_config(cfg_terms, 'gitlab_rails[\'smtp_enable\']',
                     cfg.get('smtp_enable')),
    maybe_add_config(cfg_terms, 'gitlab_rails[\'smtp_address\']',
                     cfg.get('smtp_address')),
    maybe_add_config(cfg_terms, 'gitlab_rails[\'smtp_port\']',
                     cfg.get('smtp_port')),
    maybe_add_config(cfg_terms, 'gitlab_rails[\'smtp_user_name\']',
                     cfg.get('smtp_user_name')),
    maybe_add_config(cfg_terms, 'gitlab_rails[\'smtp_password\']',
                     cfg.get('smtp_password')),
    maybe_add_config(cfg_terms, 'gitlab_rails[\'smtp_domain\']',
                     cfg.get('smtp_domain')),
    maybe_add_config(cfg_terms, 'gitlab_rails[\'smtp_enable_starttls_auto\']',
                     cfg.get('smtp_enable_starttls_auto')),
    maybe_add_config(cfg_terms, 'gitlab_rails[\'smtp_tls\']',
                     cfg.get('smtp_tls')),
    maybe_add_config(cfg_terms, 'gitlab_rails[\'incoming_email_enabled\']',
                     cfg.get('incoming_email_enabled')),
    maybe_add_config(cfg_terms, 'gitlab_rails[\'incoming_email_address\']',
                     cfg.get('incoming_email_address')),
    maybe_add_config(cfg_terms, 'gitlab_rails[\'incoming_email_email\']',
                     cfg.get('incoming_email_email')),
    maybe_add_config(cfg_terms, 'gitlab_rails[\'incoming_email_password\']',
                     cfg.get('incoming_email_password')),
    maybe_add_config(cfg_terms, 'gitlab_rails[\'incoming_email_host\']',
                     cfg.get('incoming_email_host')),
    maybe_add_config(cfg_terms, 'gitlab_rails[\'incoming_email_port\']',
                     cfg.get('incoming_email_port')),
    maybe_add_config(cfg_terms, 'gitlab_rails[\'incoming_email_ssl\']',
                     cfg.get('incoming_email_ssl')),
    maybe_add_config(cfg_terms, 'gitlab_rails[\'incoming_email_start_tls\']',
                     cfg.get('incoming_email_start_tls')),
    maybe_add_config(cfg_terms, 'gitlab_rails[\'incoming_email_mailbox_name\']',
                     cfg.get('incoming_email_mailbox_name')),

    return '; '.join(map(str, cfg_terms))
