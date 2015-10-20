from labScript import *
from cobra.model.fv import AEPg

from apicPython import createTenant
from apicPython import addSecurityDomain
from apicPython import createPrivateNetwork
from apicPython import createBridgeDomain
from apicPython import createFilter
from apicPython import createContract
from apicPython import createApplication
from apicPython import createApplicationEpg
from apicPython import connectEpgContract
from apicPython import createL4L7Cluster
from apicPython import createL4L7Device
from apicPython import createL4L7ConcreteInterface
from apicPython import createL4L7LogicalInterface


class DynamicallyCreateApplication(LabScript):

    def __init__(self):
        self.description = 'This script helps you to create an application from zero'
        self.tenant_required = True
        self.security_domains = []
        self.private_network = None
        self.bridge_domains = []
        self.filters = []
        self.contracts = []
        self.application_optional_args = None
        self.epgs = []
        self.applied_contracts = []
        self.l4l7_devices = []
        super(DynamicallyCreateApplication, self).__init__()

    def run_yaml_mode(self):
        super(DynamicallyCreateApplication, self).run_yaml_mode()
        self.security_domains = self.args.get('security_domains', [])
        self.private_network = self.args.get('private_network', [])
        self.bridge_domains = self.args.get('bridge_domains', [])
        self.filters = self.args.get('filters', [])
        self.contracts = self.args.get('contracts', [])
        self.application = self.args.get('application', {}).get('name', '')
        self.application_optional_args = self.args.get('application', {}).get('optional_args', [])
        self.epgs = self.args.get('epgs', [])
        self.applied_contracts = self.args.get('applied_contracts', [])
        self.l4l7_devices = self.args.get('l4l7_devices', [])

    def run_wizard_mode(self):
        print 'Wizard mode is not supported in this method. Please try Yaml mode.'
        sys.exit()

    def main_function(self):
        fv_tenant = self.check_if_tenant_exist(return_boolean=True)
        if not fv_tenant:
            # create a tenant
            self.mo = self.modir.lookupByDn('uni')
            fv_tenant = createTenant.create_tenant(self.mo, self.tenant)
            self.commit_change(changed_object=fv_tenant)

        # add security domains
        for security_domain in self.security_domains:
            addSecurityDomain.add_security_domain(fv_tenant, security_domain)

        # create private network
        if self.private_network:
            createPrivateNetwork.create_private_network(fv_tenant, self.private_network)

        # create bridge domains
        for bridge_domain in self.bridge_domains:
            createBridgeDomain.createBridgeDomain(fv_tenant, bridge_domain['name'], bridge_domain['subnet_ip'], self.private_network)

        # create filters
        for filter in self.filters:
            vz_filter = createFilter.create_filter(fv_tenant, filter['name'])
            if return_valid_optional_args(filter):
                for entry in return_valid_optional_args(filter):
                    createFilter.create_filter_entry(vz_filter, filter['name'], optional_args=entry)

        # create contracts
        for contract in self.contracts:
            vz_ct = createContract.create_contract(fv_tenant, contract['name'], optional_args=return_valid_optional_args(contract))
            if is_valid_key(contract, 'optional_args') and is_valid_key(contract['optional_args'], 'subjects'):
                for subject in contract['optional_args']['subjects']:
                    subject['subject'] = subject['name']
                    vz_subj = createContract.create_contract_subject(vz_ct, contract['name'], optional_args=subject)
                    if is_valid_key(subject, 'filters'):
                        for filter in subject['filters']:
                            createContract.add_filter_to_subject(vz_subj, filter)

        # create application
        if self.application:
            fv_ap = createApplication.create_application(fv_tenant, self.application, optional_args=self.application_optional_args)

        # create EPGs
        for epg in self.epgs:
            createApplicationEpg.create_application_epg(fv_ap, epg['name'], optional_args=epg['optional_args'])
        self.commit_change(changed_object=fv_tenant)

        # build n-tier application
        for contract in self.applied_contracts:
            fv_aepg = self.check_if_mo_exist('uni/tn-' + self.tenant + '/ap-' + self.application + '/epg-', contract['epg'], AEPg, description='Application EPG')
            connectEpgContract.connect_epg_contract(fv_aepg, contract['contract'], contract['type'])
            self.commit_change(changed_object=fv_aepg)

        # add L4L7 clusters/devices
        for cluster in self.l4l7_devices:

            # add cluster
            vns_ldevvip = createL4L7Cluster.create_l4l7_cluster(fv_tenant, **cluster)
            self.commit_change(changed_object=vns_ldevvip)

            # add devices to cluster
            if is_valid_key(cluster, 'devices'):
                for device in cluster['devices']:
                    if 'vmm provider' in cluster and 'vmm_domain' in cluster:
                        vns_cdev = createL4L7Device.create_l4l7_device(vns_ldevvip, vmm_provider=cluster['vmm_provider'], vmm_domain=cluster['vmm_domain'], **device)
                    else:
                        vns_cdev = createL4L7Device.create_l4l7_device(vns_ldevvip, **device)
                    self.commit_change(changed_object=vns_cdev)

                    # add concrete interfaces to devices
                    if is_valid_key(device, 'concrete_interfaces'):
                        for interface in device['concrete_interfaces']:
                            vns_cif = createL4L7ConcreteInterface.create_l4l7_concrete_interface(vns_cdev, **interface)
                            self.commit_change(changed_object=vns_cif)

            # add logical interfaces to cluster
            if is_valid_key(cluster, 'logical_interfaces'):
                for logical_interface in cluster['logical_interfaces']:
                    vns_lif = createL4L7LogicalInterface.create_l4l7_logical_interface(vns_ldevvip, logical_interface['name'], device=logical_interface['device'], label=logical_interface['label'], tenant=self.tenant, cluster=cluster['name'], cifname=logical_interface['concrete_interface'], device_package=cluster['device_package']) 
                    self.commit_change(changed_object=vns_lif)

if __name__ == '__main__':
    mo = DynamicallyCreateApplication()
