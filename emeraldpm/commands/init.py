import logging
import os

from cliff.command import Command

from emeraldpm.package import VersionSchema


class InitCommand(Command):
    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        package = {}

        name_default = os.path.basename(os.getcwd())
        package['name'] = input('package name (%s): ' % name_default) or name_default
        version_default = '1.0.0'
        package['version']  = input('version (%s): ' % version_default) or version_default
        package['description'] = input('description: ')
        package['repository_url'] = input('repository url: ')

        package_path = os.path.join(os.getcwd(), 'package.json')
        try:
            with open(package_path, 'w') as f:
                f.write(VersionSchema().dumps(package, indent=4))
        except IOError:
            self.log.exception('failed to write package.json')
