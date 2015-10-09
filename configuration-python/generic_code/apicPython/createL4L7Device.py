
from cobra.model.vns import CDev, LDevVip, CCred, CCredSecret, CMgmt, RsCDevToCtrlrP
from createMo import *

def input_key_args():
    return input_raw_input('Concrete Device Name', required=True)

def input_optional_args():
    args = {}
    # TODO
    return args

def create_l4l7_device(parent_mo, name, **args):
    """Create L4L7 Device"""
    args = args['optional_args'] if 'optional_args' in args.keys() else args
    valid_keys = ['name', 'vmName', 'vcenterName', 'devCtxLbl']
    kwargs = {k: v for k, v in args.items() if (k in valid_keys and v)}
    vns_cdev = CDev(parent_mo, name, **kwargs)
    if 'device_username' in args:
        vns_ccred = add_concrete_device_access_credentials(vns_cdev, optional_args=args)
    if 'device_password' in args:
        vns_ccredsecret = add_concrete_device_access_credentials_secret(vns_cdev, optional_args=args)
    if 'device_ip' in args or 'device_port' in args:
        vns_cmgmt = add_management_interface(vns_cdev, optional_args=args)
    if 'vmm_provider' in args and 'vmm_domain' in args and 'vmm_controller' in args:
        vns_rscdevtoctrlrp = add_source_relation_to_vmm_domain_controller_profile(vns_cdev, optional_args=args)
    return vns_cdev

def add_concrete_device_access_credentials(device_mo, **args):
    """The concrete device access credentials in the L4-L7 device cluster. The concrete device access credentials normally include a password that is not displayed and is stored in encrypted form."""
    args = args['optional_args'] if 'optional_args' in args.keys() else args
    return CCred(device_mo, name='username', value=args['device_username'])

def add_concrete_device_access_credentials_secret(device_mo, **args):
    """The secret for the concrete device access credentials in the L4-L7 device cluster. The concrete device access credentials normally include a password that is not displayed and is stored in encrypted form."""
    args = args['optional_args'] if 'optional_args' in args.keys() else args
    return CCredSecret(device_mo, name='password', value=args['device_password'])

def add_management_interface(device_mo, **args):
    """The management interface is used to manage a concrete device in the L4-L7 device cluster. The management interface is identified by a host address and port number."""
    args = args['optional_args'] if 'optional_args' in args.keys() else args
    valid_keys = ['device_ip', 'device_port']
    key_map = {'device_ip': 'host', 'device_port': 'port'}
    kwargs = {k: v for k, v in args.items() if (k in valid_keys and v)}
    kwargs = {key_map[k]: v for k, v in kwargs.items()}
    return CMgmt(device_mo, name='devMgmt', **kwargs)

def add_source_relation_to_vmm_domain_controller_profile(device_mo, **args):
    """Source relation to the vmm domain controller profile for validation."""
    args = args['optional_args'] if 'optional_args' in args.keys() else args
    valid_keys = ['vmm_provider','vmm_domain','vmm_controller']
    return RsCDevToCtrlrP(device_mo, tDn='uni/vmmp-{vmm_provider}/dom-{vmm_domain}/ctrlr-{vmm_controller}')

class CreateL4L7Device(CreateMo):
    def __init__(self):
        self.description        = 'Create an L4-L7 concrete device'
        self.tenant_required    = True
        self.contract           = None
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