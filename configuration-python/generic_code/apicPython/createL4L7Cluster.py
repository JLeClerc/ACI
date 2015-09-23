
from cobra.model.vns import LDevVip
from createMo import *

def input_key_args():
    return input_raw_input('Device Cluster Name', required=True)

def input_optional_args():
    args = {
        'context_aware': input_options('Context Aware', default='single-Context', options=['single-Context', 'multi-Context']),
        'device_type': input_options('Device Type', default='PHYSICAL', options=['PHYSICAL', 'VIRTUAL']),
        'function_type': input_options('Function Type', default='GoTo', options=['GoTo','GoThrough']),
    }
    return args

def create_l4l7_cluster(fv_tenant, name, **args):
    """Create L4L7 Cluster"""
    args = args['optional_args'] if 'optional_args' in args.keys() else args
    return LDevVip(fv_tenant, name, 
        contextAware=args['context_aware'],
        devtype=args['device_type'],
        funcType=args['function_type'])

class CreateL4L7Cluster(CreateMo):
    def __init__(self):
        self.description = 'Create an L4-L7 device cluster'
        self.tenant_required = True
        self.contract = None
        super(CreateL4L7Cluster, self).__init__()

    def set_cli_mode(self):
        super(CreateL4L7Cluster, self).set_cli_mode()
        self.parser_cli.add_argument('name', help='Cluster Name')
        self.parser_cli.add_argument('-c', '--context_aware', default='single-Context', choices=['single-Context', 'multi-Context'], 
            help='The context-awareness of the Device Cluster. Single means that the device cluster cannot be shared across multiple tenants of a given type that are hosted on the provider network. Multiple means that the device cluster can be shared across multiple tenants of a given type that you are hosting on this provider network. ')
        self.parser_cli.add_argument('-d', '--device_type', default='PHYSICAL', choices=['PHYSICAL', 'VIRTUAL'], help='Specifies whether the device cluster has PHYSICAL appliances or VIRTUAL appliances.')
        self.parser_cli.add_argument('-f', '--function_type', default='GoThrough', choices=['GoTo','GoThrough'], help='A GoTo device has a specific destination, depending on the package. A GoThrough device is a transparent device.')

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
        fv_tenant = self.check_if_tenant_exist()
        vns_ldevvip = create_l4l7_cluster(fv_tenant, self.name, optional_args=self.optional_args)

if __name__ == '__main__':
    mo = CreateL4L7Cluster()