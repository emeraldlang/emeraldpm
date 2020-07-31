from setuptools import setup


setup(
    name='emeraldpm',
    version='0.0.0',
    packages=('emeraldpm',),
    install_requires=['configobj', 'colorlog', 'cliff', 'dataclasses-json', 'requests'],
    entry_points={
        'console_scripts': [
            'emeraldpm = emeraldpm.__main__:main'
        ],
        'emeraldpm': [
            'install = emeraldpm.install:InstallCommand'
        ],
        'emeraldpm.install': [
            'config_hook = emeraldpm.config:ConfigCommandHook'
        ]
    })
