import requests

from .package import Package, Version


class API:
    def __init__(self, config):
        assert config is not None, '`config` is a required parameter.'
        self._config = config

    def download(self, name, version):
        url = '%s/api/packages/download/%s/%s/' % (
            self._config.api,
            name,
            version
        )
        res = requests.get(url)
        if res.status_code == 404:
            return None
        return res.content

    def get(self, name, version=None):
        if version is None:
            url = '%s/api/packages/package/%s/' % (
                self._config.api,
                name)
            cls = Package
        else:
            url = '%s/api/packages/package/%s/%s/' % (
                self._config.api,
                name,
                version)
            cls = Version
        res = requests.get(url)
        if res.status_code == 404:
            return None
        return cls.schema().loads(res.text)

    def publish(self, package):
        pass
