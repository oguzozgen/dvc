import os
import re
import tempfile
import posixpath

from dvc.config import Config
from dvc.logger import Logger
from dvc.exceptions import DvcException


STATUS_OK = 1
STATUS_NEW = 3
STATUS_DELETED = 4


STATUS_MAP = {
    # (local_exists, remote_exists)
    (True, True)  : STATUS_OK,
    (False, False) : STATUS_OK,
    (True, False) : STATUS_NEW,
    (False, True) : STATUS_DELETED,
}


class DataCloudError(DvcException):
    """ Data Cloud exception """
    def __init__(self, msg):
        super(DataCloudError, self).__init__('Data sync error: {}'.format(msg))



class RemoteBase(object):
    REGEX = None
    REQUIRES = {}

    def __init__(self, project, config):
        pass

    @classmethod
    def supported(cls, config):
        url = config[Config.SECTION_REMOTE_URL]
        url_ok = cls.match(url)
        deps_ok = all(cls.REQUIRES.values())
        if url_ok and not deps_ok:
            missing = [k for k,v in cls.REQUIRES.items() if v == None]
            msg = "URL \'{}\' is supported but requires these missing dependencies: {}"
            Logger.warn(msg.format(url, str(missing)))
        return url_ok and deps_ok

    @classmethod
    def match(cls, url):
        return re.match(cls.REGEX, url)

    def group(self, name):
        m = self.match(self.url)
        if not m:
            return None
        return m.group(name)

    @staticmethod
    def tmp_file(fname):
        """ Temporary name for a partial download """
        #FIXME probably better use uuid()
        return fname + '.part'

    def save_info(self, path_info):
        raise NotImplementedError

    def save(self, path_info):
        raise NotImplementedError

    def checkout(self, path_info, checksum_info):
        raise NotImplementedError

    def download(self, path_info, path, no_progress_bar=False, name=None):
        raise NotImplementedError

    def upload(self, path, path_info, name=None):
        raise NotImplementedError

    def remove(self, path_info):
        raise NotImplementedError

    def move(self, path_info):
        raise NotImplementedError

    def _makedirs(self, fname):
        dname = os.path.dirname(fname)
        try:
            os.makedirs(dname)
        except OSError as e:
            if e.errno != os.errno.EEXIST:
                raise

    def md5s_to_path_infos(self, md5s):
        raise NotImplementedError

    def exists(self, path_infos):
        raise NotImplementedError
