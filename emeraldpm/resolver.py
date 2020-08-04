from dataclasses import dataclass
import logging

from .package import PackageID, Version


@dataclass
class ResolvedPackage:
    package: dict
    selected_version: dict

    def __post_init__(self):
        valid_version = False
        for version in self.package['versions']:
            if version == self.selected_version:
                valid_version = True
                break
        if not valid_version:
            raise ValueError('`selected_version` is not a version on the provided `package`.')

    def is_version_compatible(self, version):
        # We assume that all packages with the same
        # major version will not cause any issues.
        if isinstance(version, str): 
            version = Version(version)
        elif not isinstance(version, Version):
            raise ValueError('expected version to be an instance of `str` or `Version`')
        return version.major == self.selected_version['version'].major


class Resolver:
    log = logging.getLogger(__name__)

    def __init__(self, api):
        self._api = api
        self._packages = {}

    @property
    def resolved_packages(self):
        return self._packages

    def resolve(self, package_id):
        return self._resolve_recursive(package_id)

    def resolve_many(self, package_ids):
        for package_id in package_ids:
            if not self._resolve_recursive(package_id):
                return False
        return True

    def _resolve_recursive(self, package_id, dependent_package_id=None):
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
                version = Version(package_id.version)
                selected_version = None
                # We select the maximum version that is compatible with the
                # desired version. Compatibility means equality of major versions.
                # If there's a breaking change in a minor release, go bother the
                # package owner.
                for v in package['versions']:
                    if v['version'].major == version.major:
                        selected_version = v
            else:
                selected_version = package['versions'][0]
                package_id = PackageID(package_id.name, package['versions'][0]['version'])
            self._packages[package_id.name] = ResolvedPackage(package, selected_version)
            return all([
                self._resolve_recursive(dependency_id, package_id)
                for dependency_id in self._packages[package_id.name].selected_version['dependencies']
            ])

        if package_id.version == 'latest':
            package_id = PackageID(
                package_id.name,
                self._packages[package_id.name].package['versions'][0]['version'])

        if not self._packages[package_id.name].is_version_compatible(package_id.version):
            self.log.error(
                '%s\'s dependency on %s@%s conflicts with other packages.',
                dependent_package_id.name if dependent_package_id else 'your package',
                package_id.name,
                package_id.version)
            return False

        return True
