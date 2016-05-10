""" test_handler_apt_source
Testing various config variations of the apt_source config
"""
import os
import shutil
import tempfile
import re

from cloudinit import distros
from cloudinit import util
from cloudinit.config import cc_apt_configure

from ..helpers import TestCase

UNKNOWN_ARCH_INFO = {
    'arches': ['default'],
    'failsafe': {'primary': 'http://fs-primary-default',
                 'security': 'http://fs-security-default'}
}

PACKAGE_MIRRORS = [
    {'arches': ['i386', 'amd64'],
     'failsafe': {'primary': 'http://fs-primary-intel',
                  'security': 'http://fs-security-intel'},
     'search': {
         'primary': ['http://%(ec2_region)s.ec2/',
                     'http://%(availability_zone)s.clouds/'],
         'security': ['http://security-mirror1-intel',
                      'http://security-mirror2-intel']}},
    {'arches': ['armhf', 'armel'],
     'failsafe': {'primary': 'http://fs-primary-arm',
                  'security': 'http://fs-security-arm'}},
    UNKNOWN_ARCH_INFO
]

GAPMI = distros._get_arch_package_mirror_info

def load_tfile_or_url(*args, **kwargs):
    """ load_tfile_or_url
    load file and return content after decoding
    """
    return util.decode_binary(util.read_file_or_url(*args, **kwargs).contents)

class TestAptSourceConfig(TestCase):
    """ TestAptSourceConfig
    Main Class to test apt_source configs
    """
    def setUp(self):
        super(TestAptSourceConfig, self).setUp()
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp)
        self.aptlistfile = os.path.join(self.tmp, "single-deb.list")


    @staticmethod
    def _get_default_params():
        """ get_default_params
        Get the most basic default mrror and release info to be used in tests
        """
        params = {}
        params['RELEASE'] = cc_apt_configure.get_release()
        params['MIRROR'] = "http://archive.ubuntu.com/ubuntu"
        return params


    def test_apt_source_basic(self):
        """ test_apt_source_basic
        Test Fix deb source string, has to overwrite mirror conf in params
        """
        params = self._get_default_params()
        cfg = {'source': ('deb http://archive.ubuntu.com/ubuntu'
                          ' karmic-backports'
                          ' main universe multiverse restricted'),
               'filename': self.aptlistfile}

        cc_apt_configure.add_sources([cfg], params)

        self.assertTrue(os.path.isfile(self.aptlistfile))

        contents = load_tfile_or_url(self.aptlistfile)
        self.assertTrue(re.search(r"%s %s %s %s\n" %
                                  ("deb", "http://archive.ubuntu.com/ubuntu",
                                   "karmic-backports",
                                   "main universe multiverse restricted"),
                                  contents, flags=re.IGNORECASE))


    def test_apt_source_replacement(self):
        """ test_apt_source_replace
        Test Autoreplacement of MIRROR and RELEASE in source specs
        """
        params = self._get_default_params()
        cfg = {'source': 'deb $MIRROR $RELEASE multiverse',
               'filename': self.aptlistfile}

        cc_apt_configure.add_sources([cfg], params)

        self.assertTrue(os.path.isfile(self.aptlistfile))

        contents = load_tfile_or_url(self.aptlistfile)
        self.assertTrue(re.search(r"%s %s %s %s\n" %
                                  ("deb", params['MIRROR'], params['RELEASE'],
                                   "multiverse"),
                                  contents, flags=re.IGNORECASE))

# vi: ts=4 expandtab
