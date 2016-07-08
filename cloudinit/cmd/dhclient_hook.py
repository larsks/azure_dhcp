import os
from cloudinit import stages
import json
from cloudinit import log as logging


class logDhclient():

    LOG = logging.getLogger(__name__)

    def __init__(self):
        self.hooks_dir = self._get_hooks_dir()
        print(self.hooks_dir)

    @staticmethod
    def _get_hooks_dir():
        i = stages.Init()
        return os.path.join(i.paths.get_runpath(), 'dhclient.hooks')

    def _check_hooks_dir(self):
        if not os.path.exists(self.hooks_dir):
            os.makedirs(self.hooks_dir)
        else:
            hook_files = [os.path.join(self.hooks_dir, x)
                          for x in os.listdir(self.hooks_dir)]
            print(hook_files)
            if len(hook_files) > 0:
                for hook_file in hook_files:
                    os.remove(hook_file)

    @staticmethod
    def pp_json(json_data):
        return json.dumps(json_data, indent=4)

    @staticmethod
    def get_vals(info):
        new_info = {}
        for k, v in info.iteritems():
            if k.startswith("DHCP4_") or k.startswith("new_"):
                key = (k.replace('DHCP4_', '').replace('new_', '')).lower()
                new_info[key] = v
        return new_info

    def record(self):
        envs = dict(os.environ)
        ifc_name = envs.get("interface", envs.get("DEVICE_IFACE", 'foobar'))
        ifc_file_name = os.path.join(self.hooks_dir, ifc_name + '.json')
        with open(ifc_file_name, 'w') as outfile:
            json.dump(self.get_vals(envs), outfile, indent=4)
            self.LOG.debug("Wrote dhclient options in %s", ifc_file_name)


def main():
    record = logDhclient()
    record._check_hooks_dir()
    record.record()
