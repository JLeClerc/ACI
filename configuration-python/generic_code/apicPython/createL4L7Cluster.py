
from cobra.model.vns import LDevVip, RsMDevAtt, CCred, CCredSecret, CMgmt, RsALDevToDomP
from createMo import *
import getpass
import sys

DEFAULT_CONTEXT_AWARENESS   = 'single-Context'
DEFAULT_DEVICE_TYPE         = 'PHYSICAL'
DEFAULT_FUNCTION_TYPE       = 'GoTo'

def input_key_args():
    return input_raw_input('Device Cluster Name', required=True)

def input_optional_args():
    args = {
        'contextAware': input_options('L4-L7 Device Cluster - Context Awareness', default=DEFAULT_CONTEXT_AWARENESS, options=['single-Context', 'multi-Context']),
        'devtype': input_options('L4-L7 Device Cluster - Device Type', default=DEFAULT_DEVICE_TYPE, options=['PHYSICAL', 'VIRTUAL']),
        'funcType': input_options('L4-L7 Device Cluster - Function Type', default=DEFAULT_FUNCTION_TYPE, options=['GoTo','GoThrough']),
    }
    return args

def create_l4l7_cluster(fv_tenant, name, **args):
    """Create L4L7 Cluster"""
    args = args['optional_args'] if 'optional_args' in args.keys() else args
    valid_keys = ['contextAware', 'devtype', 'funcType']
    kwargs = {k: v for k, v in args.items() if (k in valid_keys and v)}

    vns_ldevvip = LDevVip(fv_tenant, name, **kwargs)
    if 'device_package' in args:
        vns_rsmdevatt = add_metadata_source_relation(vns_ldevvip, optional_args=args)
    if 'cluster_username' in args:
        vns_ccred = add_concrete_device_access_credentials(vns_ldevvip, optional_args=args)
    if 'cluster_password' in args:
        vns_ccredsecret = add_concrete_device_access_credentials_secret(vns_ldevvip, optional_args=args)
    if 'cluster_ip' in args or 'cluster_port' in args:
        vns_cmgmt = add_management_interface(vns_ldevvip, optional_args=args)
    if 'vmm_provider' in args and 'vmm_domain' in args:
        vns_rsaldevtodomp = add_source_relation_to_vmm_domain_profile(vns_ldevvip, optional_args=args)
    return vns_ldevvip

def add_metadata_source_relation(cluster_mo, **args):
    """vnsRsMDevAtt: "A source relation to the metadata definitions for a service device type. Functions as a pointer to the device package.
        e.g: uni/infra/mDev-{device_package_vendor}-{device_package_model}-{device_package_version}
    """
    args = args['optional_args'] if 'optional_args' in args.keys() else args
    tdn = 'uni/infra/mDev-{device_package}'.format(**args)
    return RsMDevAtt(cluster_mo, tDn=tdn)

def add_concrete_device_access_credentials(cluster_mo, **args):
    """The concrete device access credentials in the L4-L7 device cluster. The concrete device access credentials normally include a password that is not displayed and is stored in encrypted form."""
    args = args['optional_args'] if 'optional_args' in args.keys() else args
    return CCred(cluster_mo, name='username', value=args['cluster_username'])

def add_concrete_device_access_credentials_secret(cluster_mo, **args):
    """The secret for the concrete device access credentials in the L4-L7 device cluster. The concrete device access credentials normally include a password that is not displayed and is stored in encrypted form."""
    args = args['optional_args'] if 'optional_args' in args.keys() else args
    return CCredSecret(cluster_mo, name='password', value=args['cluster_password'])

def add_management_interface(cluster_mo, **args):
    """The management interface is used to manage a concrete device in the L4-L7 device cluster. The management interface is identified by a host address and port number."""
    args = args['optional_args'] if 'optional_args' in args.keys() else args
    valid_keys = ['cluster_ip', 'cluster_port']
    key_map = {'cluster_ip': 'host', 'cluster_port': 'port'}
    kwargs = {k: v for k, v in args.items() if (k in valid_keys and v)}
    kwargs = {key_map[k]: v for k, v in kwargs.items()}
    return CMgmt(cluster_mo, name='devMgmt', **kwargs)

def add_source_relation_to_vmm_domain_profile(cluster_mo, **args):
    """A source relation to the VMM domain profile."""
    valid_keys = ['vmm_provider', 'vmm_domain']
    kwargs = {k: v for k, v in args.items() if (k in valid_keys and v)}
    return RsALDevToDomP(cluster_mo, tDn='uni/vmmp-{vmm_provider}/dom-{vmm_domain}')

class CreateL4L7Cluster(CreateMo):
    def __init__(self):
        self.description = 'Create an L4-L7 device cluster'
        self.tenant_required = True
        self.contract = None
        super(CreateL4L7Cluster, self).__init__()

    def set_cli_mode(self):
        super(CreateL4L7Cluster, self).set_cli_mode()
        self.parser_cli.add_argument('name', help='Cluster Name')
        self.parser_cli.add_argument('-d', '--device_package', help='Device package, e.g "Cisco-FirePOWER-1.0"', metavar='VENDOR-MODEL-VERSION')
        self.parser_cli.add_argument('-f', '--function_type', choices=['GoTo','GoThrough'], dest='funcType', help='A GoTo device has a specific destination, depending on the package. A GoThrough device is a transparent device.')
        self.parser_cli.add_argument('-t', '--device_type', choices=['PHYSICAL', 'VIRTUAL'], dest='devtype', help='Specifies whether the device cluster has PHYSICAL appliances or VIRTUAL appliances.')
        self.parser_cli.add_argument('-u1', '--username', dest='cluster_username', help='Username for the L4-L7 cluster.')
        self.parser_cli.add_argument('-u2', '--password', dest='cluster_password', help='Password for the L4-L7 cluster.')
        self.parser_cli.add_argument('-i', '--ip', dest='cluster_ip', help='IP Address of the L4-L7 cluster host.')
        self.parser_cli.add_argument('-p', '--port', dest='cluster_port', help='Port of the L4-L7 cluster host.')
        self.parser_cli.add_argument('-x', '--context_aware', choices=['single-Context', 'multi-Context'], dest='contextAware', 
            help='The context-awareness of the Device Cluster. Single means that the device cluster cannot be shared across multiple tenants of a given type that are hosted on the provider network. Multiple means that the device cluster can be shared across multiple tenants of a given type that you are hosting on this provider network. ')

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