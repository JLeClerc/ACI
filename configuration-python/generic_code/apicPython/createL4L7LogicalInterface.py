
from cobra.model.vns import CDev, LIf, RsMetaIf, RsCIfAtt, RsCIfAttN
from createMo import *

def input_key_args():
    return input_raw_input('Concrete Interface Name', required=True)

def input_optional_args():
    args = {}
    # TODO
    return args

def create_l4l7_logical_interface(parent_mo, name, **args):
    """The logical interface is associated with a set of concrete interfaces from the L4-L7 device cluster. This is used to define the connection between a service graph and device interfaces."""
    args = args['optional_args'] if 'optional_args' in args.keys() else args
    valid_keys = ['name', 'encap']
    kwargs = {k: v for k, v in args.items() if (k in valid_keys and v)}
    vns_lif = LIf(parent_mo, name, **kwargs)
    if 'interface_label' in args:
        vns_rsmetaif = add_source_relation_to_interface_label(vns_lif, device_package=args['device_package'], label= args['label'])
    if 'concrete_interface':
        vns_rscifatt = add_association_to_concrete_interface(vns_lif, tenant=args['tenant'], cluster=args['cluster'], device=args['device'], cifname=args['cifname'])
    return vns_lif

def add_source_relation_to_interface_label(logical_interface_mo, **args):
    """A source relation to an interface label. e.g: tDn='uni/infra/mDev-Cisco-FirePOWER-1.0/mIfLbl-external' """
    valid_keys = ['device_package', 'label']
    kwargs = {k: v for k, v in args.items() if (k in valid_keys and v)}
    return RsMetaIf(logical_interface_mo, tDn='uni/infra/mDev-{device_package}/mIfLbl-{label}'.format(**kwargs))

def add_association_to_concrete_interface(logical_interface_mo, **args):
    """Association to a set of concrete interfaces from the device in the cluster."""
    valid_keys = ['tenant', 'cluster', 'device', 'cifname']
    kwargs = {k: v for k, v in args.items() if (k in valid_keys and v)}
    return RsCIfAtt(logical_interface_mo, tDn='uni/tn-{tenant}/lDevVip-{cluster}/cDev-{device}/cIf-{cifname}'.format(**kwargs))

class CreateL4L7ConcreteInterface(CreateMo):
    def __init__(self):
        self.description        = 'Create an L4-L7 concrete device'
        self.tenant_required    = True
        self.contract           = None
        super(CreateL4L7ConcreteInterface, self).__init__()