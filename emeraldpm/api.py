import progressbar
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
        res = requests.get(url, stream=True)
        if res.status_code == 404:
            return None
        block_size = 1024
        data = b''
        total_size_in_bytes= int(res.headers.get('content-length', 0))
        if self._config.show_progress_bar and total_size_in_bytes > (40 * block_size):
            bytes_read = 0
            widgets=[
                progressbar.Percentage(),
                ' ',
                progressbar.Bar(),
                ' ',
                progressbar.Timer(),
                ' ',
                progressbar.ETA(),
            ]
            with progressbar.ProgressBar(
                    max_value=total_size_in_bytes,
                    redirect_stdout=True,
                    widgets=widgets) as bar:
                for block in res.iter_content(block_size):
                    data += block
                    bytes_read += len(block)
                    bar.update(bytes_read)
        else:
            for block in res.iter_content(block_size):
                data += block

        return data

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
