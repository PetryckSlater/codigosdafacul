#!/usr/bin/env python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import Intf, TCLink
from mininet.node import Node
from mininet.log import setLogLevel, info
from mininet.cli import CLI

class LinuxRouter(Node):
    "Um nó com encaminhamento IP habilitado."

    def config(self, **params):
        super(LinuxRouter, self).config(**params)
        # Habilitar o encaminhamento no roteador
        self.cmd('sysctl net.ipv4.ip_forward=1')

    def terminate(self):
        self.cmd('sysctl net.ipv4.ip_forward=0')
        super(LinuxRouter, self).terminate()

class NetworkTopo(Topo):
    "Um LinuxRouter conectando três sub-redes IP"

    def build(self, **_opts):

        # Definição do roteador e suas interfaces
        defaultIP = '10.0.1.1/24'  # IP address for r0-eth1
        router = self.addNode('r0', cls=LinuxRouter, ip=defaultIP)

        # Adicionando switches
        s1, s2 = [self.addSwitch(s) for s in ('s1', 's2')]

        # Adicionando hosts
        h1 = self.addHost('h1', ip='10.0.1.100/24', defaultRoute='via 10.0.1.1')
        h2 = self.addHost('h2', ip='10.0.2.100/24', defaultRoute='via 10.0.2.1')

        # Parâmetros do link
        enlace = {'cls': TCLink}

        # Conectando o roteador às redes
        self.addLink(s1, router, intfName2='r0-eth1', **enlace)
        self.addLink(s2, router, intfName2='r0-eth2', params2={'ip': '10.0.2.1/24'}, **enlace)

        # Conectando hosts aos switches
        self.addLink(h1, s1, **enlace)
        self.addLink(h2, s2, **enlace)

def run():
    "Testar o roteador Linux"
    topo = NetworkTopo()
    net = Mininet(topo=topo, waitConnected=True)

    # Associar a interface física 'eth0' aos switches do Mininet
    Intf('eth0', node=net['s1'])

    net.start()

    # Adicionando rotas ao roteador
    net['r0'].cmd('ip route add 172.17.0.0/16 via 192.168.56.101 dev r0-eth1')
    net['r0'].cmd('ip route add 172.16.0.0/16 via 192.168.56.101 dev r0-eth2')

    info('*** Tabela de Roteamento no Roteador:\n')
    info(net['r0'].cmd('route'))

    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run()
