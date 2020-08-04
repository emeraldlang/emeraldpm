import os
import sys

from configobj import ConfigObj
from validate import Validator


def _get_home_dir():
    home = os.environ.get('HOME')
    user = os.environ.get('LOGNAME') or\
        os.environ.get('USER') or\
        os.environ.get('LNAME') or\
        os.environ.get('USERNAME')
    if sys.platform == 'win32':
        return os.environ.get('USERPROFILE') or home
    elif sys.platform == 'darwin':
        return home or ('/Users/%s' % user if user else None)
    elif sys.platform == 'linux':
        return home or '/root' if (os.getuid() == 0) else ('/home/%s' % user if user else None)

    return home 


class Config:
    def __init__(self, api=None, token=None, show_progress_bar=None):
        configspec = '''
        [api]
            api=string(default='https://emeraldpm.io')
            token=string(default=None)
        [logging]
            show_progress_bar=boolean(default=True)
        '''.splitlines()
        config_file = os.path.join(
            _get_home_dir(),
            '.emeraldpmc')
        self._config_obj = ConfigObj(config_file, configspec=configspec)
        self._config_obj.validate(Validator())

        api_config = self._config_obj['api']
        self._api = (api or api_config['api']).rstrip('/')
        self._token = token or api_config['token']

        logging_config = self._config_obj['logging']
        if show_progress_bar is not None:
            self._show_progress_bar = show_progress_bar
        else:
            self._show_progress_bar = logging_config['show_progress_bar']

    @property
    def api(self):
        return self._api

    @api.setter
    def api(self, val):
        self._api = self._config_obj['api']['api'] = val.rstrip('/')

    @property
    def token(self):
        return self._token

    @token.setter
    def token(self, val):
        self._token = self._config_obj['api']['token'] = val

    @property
    def show_progress_bar(self):
        return self._show_progress_bar

    @show_progress_bar.setter
    def show_progress_bar(self, val):
        self._show_progress_bar = self._config_obj['logging']['show_progress_bar'] = val
