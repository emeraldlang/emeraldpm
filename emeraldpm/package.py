from collections import namedtuple
from dataclasses import asdict, dataclass, field
from dataclasses_json import dataclass_json, config
import json
import os
from marshmallow import fields
from typing import List, Optional


PackageID = namedtuple('PackageID', 'name version', defaults=('latest',))


class VersionInfo:
    def __init__(self, value):
        split_version = value.split('.')
        if len(split_version) > 4:
            raise ValueError('Version number can consist of 4 components: major, minor, patch, build.')
        self._version = list(int(x) for x in (list(split_version) + [0] * 3)[:4])
        if any([x < 0 or x > 255 for x in self._version]):
            raise ValueError('Version number <major.minor.patch.build> components must be in the '
                             'inclusive range 0, 255')

    @property
    def major(self):
        return self._version[0]

    def inc_major(self):
        self._version[0] += 1

    @property
    def minor(self):
        return self._version[1]

    def inc_minor(self):
        self._version[1] += 1

    @property
    def patch(self):
        return self._version[2]

    def inc_patch(self):
        self._version[2] += 1

    @property
    def build(self):
        return self._version[3]

    def inc_build(self):
        self._version[3] += 1

    def __int__(self):
        major, minor, patch, build = self._version
        num = (major << 24) | (minor << 16) | (patch << 8) | build
        return num - 2**31

    def __str__(self):
        ei = 3 if self._version[3] else 2
        return '.'.join([str(x) for x in self._version[:ei + 1]])

    def __eq__(self, other):
        return int(self) == int(other)

    def __ne__(self, other):
        return not (self == other)

    def __gt__(self, other):
        return int(self) > int(other)

    def __ge__(self, other):
        return int(self) >= int(other)

    def __lt__(self, other):
        return int(self) < int(other)

    def __le__(self, other):
        return int(self) <= int(other)



@dataclass_json()
@dataclass
class Version:
    name: str
    version: VersionInfo = field(
        metadata=config(
            encoder=lambda x: str(x),
            decoder=lambda x: VersionInfo(x),
            mm_field=fields.String()
        ))
    description: str
    repository_url: str
    dependencies: List[PackageID] = field(
        metadata=config(
            encoder=lambda x: print('shit'),
            mm_field=fields.Raw()
        )
    )
    archive: str = None
    readme: str = None

    def get_schema_write_exclusions(self):
        exclusions = ['archive']
        if not self.readme:
            exclusions.append('readme')
        if not self.dependencies:
            exclusions.append('dependencies')
        return tuple(exclusions)


@dataclass_json
@dataclass
class Package:
    name: str
    owner: str
    versions: List[Version]
