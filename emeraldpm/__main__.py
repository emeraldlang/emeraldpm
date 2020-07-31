import sys

import coloredlogs
from cliff.app import App
from cliff.commandmanager import CommandManager


class EmeraldPMApp(App):
    def __init__(self):
        super().__init__(
            description='Emerald Package Manager',
            version='0.0.0',
            command_manager=CommandManager('emeraldpm'),
            deferred_help=True)


def main(argv=sys.argv[1:]):
    app = EmeraldPMApp()
    return app.run(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
