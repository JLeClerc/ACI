
from cobra.model.vns import LDevVip
from createMo import *

def input_key_args():
    return input_raw_input('Device Cluster Name', required=True)

def input_optional_args():
    args = {}
    # TODO
    return args

def create_l4l7_cluster(fv_tenant, name, **args):
    """Create L4L7 Cluster"""
    return LDevVip(fv_tenant, name)

class CreateL4L7Cluster(CreateMo):
    def __init__(self):
        self.description = 'Create an L4-L7 device cluster'
        self.tenant_required = True
        self.contract = None
        super(CreateL4L7Cluster, self).__init__()

    def set_cli_mode(self):
        super(CreateL4L7Cluster, self).set_cli_mode()
        self.parser_cli.add_argument('name', help='Cluster Name')

    def read_key_args(self):
        self.tenant = self.args.pop('tenant')
        self.name = self.args.pop('name')

    def wizard_mode_input_args(self):
        self.args['name'] = input_key_args()
        if not self.delete:
            self.args['optional_args'] = input_optional_args()

    def delete_mo(self):
        self.check_if_mo_exist('uni/tn-'+self.tenant+'/lDevVip-', self.name, LDevVip, description='LDevVip')
        super(CreateL4L7Cluster, self).delete_mo()

    def main_function(self):
        # Query a tenant
        fv_tenant = self.check_if_tenant_exist()

        vns_ldevvip = create_l4l7_cluster(fv_tenant, self.name, optional_args=self.optional_args)

if __name__ == '__main__':
    mo = CreateL4L7Cluster()