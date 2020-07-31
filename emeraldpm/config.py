import os
import sys

from cliff.hooks import CommandHook

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
    def __init__(self, api=None, token=None):
        configspec = '''
        api=string(default='https://emeraldpm.io')
        token=string(default=None)
        '''.splitlines()
        config_file = os.path.join(
            _get_home_dir(),
            '.emeraldpmc')
        self._config_obj = ConfigObj(config_file, configspec=configspec)
        self._config_obj.validate(Validator())

        self._api = (api or self._config_obj['api']).rstrip('/')
        self._token = token or self._config_obj['token']

    @property
    def api(self):
        return self._api

    @api.setter
    def api(self, val):
        self._api = self._config_obj['api'] = val.rstrip('/')

    @property
    def token(self):
        return self._token

    @token.setter
    def token(self, val):
        self._token = self._config_obj['token'] = val

    @classmethod
    def add_args_to_parser(cls, parser):
        parser.add_argument('--api')
        parser.add_argument('--token')

    @classmethod
    def from_parsed_args(cls, parsed_args): 
        return cls(**{
            'api': parsed_args.api,
            'token': parsed_args.token
        })


class ConfigCommandHook(CommandHook):
    def get_parser(self, parser):
        Config.add_args_to_parser(parser)
        return parser

    def get_epilog(self):
        return 'add emeraldpmc configuration options'

    def before(self, parsed_args):
        parsed_args.config = Config.from_parsed_args(parsed_args)
        return parsed_args

    def after(self, parsed_args, return_code):
        pass
