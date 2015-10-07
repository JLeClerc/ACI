
from cobra.model.vns import CDev, CIf, RsCIfPathAtt
from createMo import *

def input_key_args():
    return input_raw_input('Concrete Interface Name', required=True)

def input_optional_args():
    args = {}
    # TODO
    return args

def create_l4l7_concrete_interface(parent_mo, name, **args):
    """Create L4L7 Concrete Interface"""
    args = args['optional_args'] if 'optional_args' in args.keys() else args
    valid_keys = ['name', 'vnicName']
    kwargs = {k: v for k, v in args.items() if (k in valid_keys and v)}
    vns_cif = CIf(parent_mo, name, **kwargs)
    if 'path' in args:
        vns_rscifpathatt = add_source_relation_to_path_endpoint(vns_cif, args['path'])
    return vns_cif

def add_source_relation_to_path_endpoint(concrete_interface_mo, path):
    """A source relation to a path endpoint. e.g: 'topology/pod-1/paths-1001/pathep-[eth1/10]' """
    return RsCIfPathAtt(concrete_interface_mo, tDn=path)

class CreateL4L7ConcreteInterface(CreateMo):
    def __init__(self):
        self.description        = 'Create an L4-L7 concrete device'
        self.tenant_required    = True
        self.contract           = None
        super(CreateL4L7ConcreteInterface, self).__init__()