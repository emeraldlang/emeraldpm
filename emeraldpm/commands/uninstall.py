import os

from cliff.command import Command

from emeraldpm.api import API
from emeraldpm.config import Config
from emeraldpm.package import Version, VersionInfo, Package, PackageID


class UninstallCommand(Command):
    "Uninstalls a package and its dependencies"

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument('packages', nargs='+')
        parser.add_argument('--api')
        parser.add_argument('--token')
        return parser

    def take_action(self, parsed_args):
        pass
