from collections.abc import Iterable
from dataclasses import dataclass
import io
import logging
import os
import tempfile
from typing import List
import zipfile

from cliff.command import Command

from emeraldpm.api import API
from emeraldpm.config import Config
from emeraldpm.package import Version, VersionInfo, Package, PackageID


@dataclass
class _PackageToInstall:
    package: Package
    selected_version: Version

    def __post_init__(self):
        valid_version = False
        for version in self.package.versions:
            if version == self.selected_version:
                valid_version = True
                break
        if not valid_version:
            raise ValueError('`selected_version` is not a version on the provided `package`.')

    def is_version_compatible(self, version):
        # We assume that all packages with the same
        # major version will not cause any issues.
        if isinstance(version, str): 
            version = VersionInfo(version)
        elif not isinstance(version, VersionInfo):
            return False
        return version.major == self.selected_version.version.major


class InstallCommand(Command):
    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument('packages', nargs='*')
        parser.add_argument('--api')
        parser.add_argument('--token')
        parser.add_argument('--show_progress_bar')
        return parser

    def take_action(self, parsed_args):
        config = Config(**{
            'api': parsed_args.api,
            'token': parsed_args.token,
            'show_progress_bar': parsed_args.show_progress_bar
        })
        self._api = API(config)

        package_path = os.path.join(os.getcwd(), 'package.json')
        try:
            with open(package_path, 'r') as f:
                package = Version.schema().loads(f.read())
        except IOError:
            self.log.exception('failed to read package.json')
            return

        if parsed_args.packages:
            package.dependencies += [
                PackageID(*package_id.split('@')) for package_id in parsed_args.packages
            ]
        self._packages = {}
        self.log.info('getting package info for %d packages', len(package.dependencies))
        for package_id in package.dependencies:
            if not self._get_package(package_id):
                return

        modules_dir = os.path.join(os.getcwd(), 'emerald_modules')
        os.makedirs(modules_dir, exist_ok=True)
        for package_to_install in self._packages.values():
            name = package_to_install.package.name
            version = str(package_to_install.selected_version.version)

            output_path = os.path.join(modules_dir, name)
            if os.path.exists(os.path.join(output_path, 'package.json')):
                continue

            self.log.info('downloading package %s@%s', name, version)
            data = self._api.download(name, version)

            with zipfile.ZipFile(io.BytesIO(data)) as zf:
                zf.extractall(output_path)

        if parsed_args.packages:
            try:
                with open(package_path, 'w') as f:
                    schema = Version.schema(exclude=package.get_schema_write_exclusions())
                    f.write(schema.dumps(package, indent=4))
            except IOError:
                self.log.exception('failed to write package.json')

    def _get_package(self, package_id, dependent_package_id=None):
        if package_id.name not in self._packages:
            self.log.debug(
                'getting package info for %s@%s...',
                package_id.name,
                package_id.version)
            package = self._api.get(package_id.name)
            if package == None:
                self.log.error('no such package %s', package_id.name)
                return False
            if package_id.version != 'latest':
                version = VersionInfo(package_id.version)
                selected_version = None
                # We select the maximum version that is compatible with the
                # desired version. Compatibility means equality of major versions.
                # If there's a breaking change in a minor release, go bother the
                # package owner.
                for v in package.versions:
                    if v.version.major == version.major:
                        selected_version = v
            else:
                selected_version = package.versions[0]
                package_id = PackageID(package_id.name, package.versions[0].version)
            self._packages[package.name] = _PackageToInstall(package, selected_version)
            return all([
                self._get_package(dependency_id, package_id)
                for dependency_id in self._packages[package_id.name].selected_version.dependencies
            ])

        if package_id.version == 'latest':
            package_id = PackageID(
                package_id.name,
                self._packages[package_id.name].package.versions[0].version)

        if not self._packages[package_id.name].is_version_compatible(package_id.version):
            self.log.error(
                '%s\'s dependency on %s@%s conflicts with other packages.',
                dependent_package_id.name if dependent_package_id else 'your package',
                package_id.name,
                package_id.version)
            return False

        return True