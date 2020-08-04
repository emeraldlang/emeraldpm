import io
import logging
import os
import zipfile

from cliff.command import Command

from emeraldpm.api import API
from emeraldpm.config import Config
from emeraldpm.package import PackageID, VersionSchema
from emeraldpm.resolver import Resolver


class InstallCommand(Command):
    "Installs a package and its dependencies"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument('packages', nargs='*')
        parser.add_argument('--api')
        parser.add_argument('--token')
        parser.add_argument('--show_progress_bar')
        return parser

    def take_action(self, parsed_args):
        package_path = os.path.join(os.getcwd(), 'package.json')
        try:
            with open(package_path, 'r') as f:
                package = VersionSchema().loads(f.read())
        except IOError:
            self.log.exception('failed to read package.json')
            return

        to_resolve = set(package['dependencies'])
        if parsed_args.packages:
            try:
                to_resolve = to_resolve.union(set(
                    PackageID(*package_id.split('@')) for package_id in parsed_args.packages
                ))
            except ValueError:
                self.log.exception('invalid version string provided')
                return

        config = Config(**{
            'api': parsed_args.api,
            'token': parsed_args.token,
            'show_progress_bar': parsed_args.show_progress_bar
        })
        api = API(config)
        resolver = Resolver(api)
        self.log.info('resolving %d packages', len(to_resolve))
        if not resolver.resolve_many(to_resolve):
            return

        modules_dir = os.path.join(os.getcwd(), 'emerald_modules')
        os.makedirs(modules_dir, exist_ok=True)
        for package_to_install in resolver.resolved_packages.values():
            name = package_to_install.package['name']
            version = str(package_to_install.selected_version['version'])

            output_path = os.path.join(modules_dir, name)
            dependency_package_path = os.path.join(output_path, 'package.json') 
            if os.path.exists(dependency_package_path):
                with open(dependency_package_path, 'r') as f:
                    dependency = VersionSchema().loads(f.read())
                if dependency.version == package_to_install.selected_version['version']:
                    continue

            self.log.info('downloading package %s@%s', name, version)
            data = api.download(name, version)

            with zipfile.ZipFile(io.BytesIO(data)) as zf:
                zf.extractall(output_path)

        package['dependencies'] = [
            PackageID(
                dependency.selected_version['name'],
                str(dependency.selected_version['version']))
            for dependency in resolver.resolved_packages.values()
        ]
        try:
            with open(package_path, 'w') as f:
                f.write(VersionSchema().dumps(package, indent=4))
        except IOError:
            self.log.exception('failed to write package.json')
