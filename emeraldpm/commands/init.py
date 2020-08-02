import logging
import os

from cliff.command import Command

from emeraldpm.package import Version, VersionInfo


class InitCommand(Command):
    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        name_default = os.path.basename(os.getcwd())
        name = input('package name (%s): ' % name_default) or name_default
        version_default = VersionInfo('1.0.0')
        version_input = input('version (%s): ' % version_default)
        if version_input:
            try:
                version = VersionInfo(version_input)
            except ValueError:
                self.log.exception('invalid version string')
                return
        else:
            version = version_default
        description = input('description: ')
        repository_url = input('repository url: ')

        package = Version(
            name=name,
            version=version,
            description=description,
            repository_url=repository_url)
        package_path = os.path.join(os.getcwd(), 'package.json')
        try:
            with open(package_path, 'w') as f:
                schema = Version.schema(exclude=package.get_schema_write_exclusions())
                f.write(schema.dumps(package, indent=4))
        except IOError:
            self.log.exception('failed to write package.json')
