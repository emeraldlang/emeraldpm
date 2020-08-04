from collections import namedtuple

from marshmallow import Schema, fields, post_dump, ValidationError


class Version:
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


class _VersionField(fields.Field):
    def _deserialize(self, value, *args, **kwargs):
        try:
            return Version(value)
        except ValueError as e:
            raise ValidationError('Not a valid version') from e

    def _serialize(self, value, *args, **kwargs):
        return str(value)


PackageID = namedtuple('PackageID', 'name version', defaults=('latest',))


class _PackageIDField(fields.Field):
    def _deserialize(self, value, *args, **kwargs):
        return PackageID(*value.split('@'))

    def _serialize(self, value, *args, **kwargs):
        return '%s@%s' % (value.name, value.version)


class VersionSchema(Schema):
    name = fields.Str(required=True)
    version = _VersionField(required=True)
    description = fields.Str(required=False, missing=None)
    repository_url = fields.Str(required=False, missing=None)
    archive = fields.URL(required=False, load_only=True, missing=None)
    readme = fields.Str(required=False, missing=None)
    dependencies = fields.List(_PackageIDField(), missing=lambda: [])

    @post_dump
    def remove_values(self, data, many):
        return {
            key: value for key, value in data.items() if value
        }

    class Meta:
        ordered = True


class PackageSchema(Schema):
    name = fields.Str(required=True)
    owner = fields.Str(required=True)
    versions = fields.List(fields.Nested(VersionSchema))

    class Meta:
        ordered = True
