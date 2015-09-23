
from cobra.model.vns import CDev, LDevVip
from createMo import *

def input_key_args():
    return input_raw_input('Concrete Device Name', required=True)

def input_optional_args():
    args = {}
    # TODO
    return args

def create_l4l7_device(parent_mo, name, **args):
    """Create L4L7 Device"""
    return CDev(parent_mo, name)

class CreateL4L7Device(CreateMo):
    def __init__(self):
        self.description = 'Create an L4-L7 concrete device'
        self.tenant_required = True
        self.contract = None
        super(CreateL4L7Device, self).__init__()

    def set_cli_mode(self):
        super(CreateL4L7Device, self).set_cli_mode()
        self.parser_cli.add_argument('cluster_name', help='Name of the parent L4-L7 Device Cluster')
        self.parser_cli.add_argument('name', help='Device Name')

    def read_key_args(self):
        self.tenant         = self.args.pop('tenant')
        self.cluster_name   = self.args.pop('cluster_name')
        self.name           = self.args.pop('name')

    def wizard_mode_input_args(self):
        self.args['name'] = input_key_args()
        if not self.delete:
            self.args['optional_args'] = input_optional_args()

    def delete_mo(self):
        self.check_if_mo_exist('uni/tn-{tenant}/lDevVip-{cluster_name}/cDev-'.format(**self.__dict__), self.name, CDev, description='CDev')
        super(CreateL4L7Device, self).delete_mo()

    def main_function(self):
        # Query a tenant
        parent_mo = self.check_if_mo_exist('uni/tn-{tenant}/lDevVip-'.format(**self.__dict__), self.cluster_name, LDevVip, description='LDevVip')
        vns_cdev = create_l4l7_device(parent_mo, self.name, optional_args=self.optional_args)

if __name__ == '__main__':
    mo = CreateL4L7Device()