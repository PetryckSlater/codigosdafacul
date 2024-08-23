#!/usr/bin/env python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import Intf
from mininet.node import Node
from mininet.link import TCLink
from mininet.log import setLogLevel, info
from mininet.cli import CLI

class LinuxRouter(Node):
    "Um nó com encaminhamento IP habilitado."

    # pylint: disable=arguments-differ
    def config(self, **params):
        super(LinuxRouter, self).config(**params)
        # Habilitar o encaminhamento no roteador
        self.cmd('sysctl net.ipv4.ip_forward=1')

    def terminate(self):
        # Desabilitar o encaminhamento quando o roteador for encerrado
        self.cmd('sysctl net.ipv4.ip_forward=0')
        super(LinuxRouter, self).terminate()


class NetworkTopo(Topo):
    "Um LinuxRouter conectando três sub-redes IP"

    # pylint: disable=arguments-differ
    def build(self, **_opts):
        # IP padrão para o roteador
        defaultIP = '10.0.1.1/24'

        # Adicionar o roteador com o IP padrão
        router = self.addNode('r0', cls=LinuxRouter, ip=defaultIP)

        # Adicionar switches
        s1, s2 = [self.addSwitch(s) for s in ('s1', 's2')]

        # Adicionar hosts com seus respectivos IPs e rotas padrão
        h1 = self.addHost('h1', ip='10.0.1.100/24', defaultRoute='via 10.0.1.1')
        h2 = self.addHost('h2', ip='10.0.2.100/24', defaultRoute='via 10.0.2.1')

        # Parâmetros para o link
        link_opts = {'cls': TCLink}

        # Conectar o roteador aos switches
        self.addLink(s1, router, intfName2='r0-eth1', **link_opts)
        self.addLink(s2, router, intfName2='r0-eth2', params2={'ip': '10.0.2.1/24'}, **link_opts)

        # Conectar os hosts aos switches
        self.addLink(h1, s1, **link_opts)
        self.addLink(h2, s2, **link_opts)

def run():
    "Testar roteador Linux"
    topo = NetworkTopo()
    net = Mininet(topo=topo, waitConnected=True)

    # Conectar interfaces externas ao switch
    Intf('enp2s0', node=net['s1'])
    Intf('enp3s0', node=net['s2'])

    # Iniciar a rede
    net.start()
    
    # Exibir tabela de roteamento no roteador
    info('*** Tabela de Roteamento no Roteador:\n')
    info(net['r0'].cmd('route'))
    
    # Iniciar CLI do Mininet para controle interativo
    CLI(net)
    
    # Parar a rede
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run()
