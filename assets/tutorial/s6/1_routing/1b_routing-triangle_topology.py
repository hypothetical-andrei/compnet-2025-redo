"""
Topologie Mininet: Triunghi de 3 routere + 2 hosturi
h1 conectat la r1, h3 conectat la r3, și trei linkuri r1–r2, r2–r3, r1–r3.

Ruterul este un Node Mininet care activează IP forwarding.
Studentul va configura rute statice manual.
"""

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import setLogLevel


class LinuxRouter(Node):
    """Un nod Mininet cu IP forwarding activat (se comportă ca un router Linux real)."""
    def config(self, **params):
        super(LinuxRouter, self).config(**params)
        # Activăm forwardarea IPv4
        self.cmd("sysctl -w net.ipv4.ip_forward=1")

    def terminate(self):
        super(LinuxRouter, self).terminate()


class TriangleRoutingTopo(Topo):
    """Topologia triunghiului r1–r2–r3, plus hosturi h1 și h3."""
    def build(self):

        # Cream routerele
        r1 = self.addNode('r1', cls=LinuxRouter)
        r2 = self.addNode('r2', cls=LinuxRouter)
        r3 = self.addNode('r3', cls=LinuxRouter)

        # Hosturi
        h1 = self.addHost('h1')
        h3 = self.addHost('h3')

        # Linkuri host-router
        self.addLink(h1, r1)
        self.addLink(h3, r3)

        # Linkurile triunghiului
        self.addLink(r1, r2)
        self.addLink(r2, r3)
        self.addLink(r1, r3)


def run():
    """
    Creează rețeaua, îi setează adrese IP și lansează CLI-ul pentru configurări.
    Rutele NU sunt adăugate automat — studentul trebuie să le scrie manual.
    """
    topo = TriangleRoutingTopo()
    net = Mininet(topo=topo, link=TCLink, controller=None)
    net.start()

    # Referințe către noduri
    r1, r2, r3 = net.get('r1'), net.get('r2'), net.get('r3')
    h1, h3 = net.get('h1'), net.get('h3')

    # ------------------------------
    # Configurări IPv4 pe interfețe
    # ------------------------------

    # h1 <-> r1
    h1.setIP("10.0.1.2/30", intf="h1-eth0")
    r1.setIP("10.0.1.1/30", intf="r1-eth0")

    # r1 <-> r2
    r1.setIP("10.0.12.1/30", intf="r1-eth1")
    r2.setIP("10.0.12.2/30", intf="r2-eth0")

    # r2 <-> r3
    r2.setIP("10.0.23.1/30", intf="r2-eth1")
    r3.setIP("10.0.23.2/30", intf="r3-eth0")

    # r1 <-> r3
    r1.setIP("10.0.13.1/30", intf="r1-eth2")
    r3.setIP("10.0.13.2/30", intf="r3-eth1")

    # r3 <-> h3
    r3.setIP("10.0.3.1/30", intf="r3-eth2")
    h3.setIP("10.0.3.2/30", intf="h3-eth0")

    print("\n=== Topologia a fost pornită ===")
    print("Configurațiile IP sunt setate.")
    print("Studentul trebuie să adauge rute statice manual.")
    print("Folosește 'r1 ip route', 'r2 ip route', etc.\n")

    CLI(net)
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    run()
