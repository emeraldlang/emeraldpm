import logging
import sys

from cliff.app import App
from cliff.commandmanager import CommandManager
from colorlog import ColoredFormatter


class EmeraldPMApp(App):
    CONSOLE_MESSAGE_FORMAT = '%(log_color)s%(levelname)-8s%(reset)s %(name)s: %(white)s%(message)s'

    def __init__(self):
        super().__init__(
            description='Emerald Package Manager',
            version='0.0.0',
            command_manager=CommandManager('emeraldpm'),
            deferred_help=True)

    def configure_logging(self):
        root_logger = logging.getLogger('')
        root_logger.setLevel(logging.DEBUG)

        if self.options.log_file:
            file_handler = logging.FileHandler(
                filename=self.options.log_file,
            )
            formatter = logging.Formatter(self.LOG_FILE_MESSAGE_FORMAT)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)

        console = logging.StreamHandler(self.stderr)
        console_level = {0: logging.WARNING,
                         1: logging.INFO,
                         2: logging.DEBUG,
                         }.get(self.options.verbose_level, logging.DEBUG)
        console.setLevel(console_level)
        formatter = ColoredFormatter(
            self.CONSOLE_MESSAGE_FORMAT,
            datefmt=None,
            reset=True,
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white'
        })
        console.setFormatter(formatter)
        root_logger.addHandler(console)


def main(argv=sys.argv[1:]):
    app = EmeraldPMApp()
    return app.run(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
