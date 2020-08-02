from setuptools import setup


setup(
    name='emeraldpm',
    version='0.0.0',
    packages=('emeraldpm',),
    install_requires=['configobj', 'colorlog', 'cliff', 'dataclasses-json', 'progressbar2', 'requests'],
    entry_points={
        'console_scripts': [
            'emeraldpm = emeraldpm.__main__:main'
        ],
        'emeraldpm': [
            'init = emeraldpm.commands.init:InitCommand',
            'install = emeraldpm.commands.install:InstallCommand',
            'version = emeraldpm.commands.version:VersionCommand'
        ]
    })
