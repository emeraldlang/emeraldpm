import argparse
import logging
import os

from cliff.command import Command

from emeraldpm.package import Version, VersionSchema


def _check_version(value):
    if value in ('major', 'minor', 'patch', 'build'):
        return value
    try:
        return Version(value)
    except ValueError:
        raise argparse.ArgumentTypeError('%s is not a valid version' % value)


class VersionCommand(Command):
    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'version',
            type=_check_version,
            help='should be a valid version string, major, minor, patch or build')
        return parser

    def take_action(self, parsed_args):
        package_path = os.path.join(os.getcwd(), 'package.json')
        try:
            with open(package_path, 'r') as f:
                package = VersionSchema().loads(f.read())
        except IOError:
            self.log.exception('failed to read package.json')
            return

        if isinstance(parsed_args.version, str):
            if parsed_args.version == 'major':
                package['version'].inc_major()
            elif parsed_args.version == 'minor':
                package['version'].inc_minor()
            elif parsed_args.version == 'patch':
                package['version'].inc_patch()
            elif parsed_args.version == 'build':
                package['version'].inc_build()
        else:
            package['version'] = parsed_args.version

        try:
            with open(package_path, 'w') as f:
                f.write(VersionSchema().dumps(package, indent=4))
        except IOError:
            self.log.exception('failed to write package.json')
