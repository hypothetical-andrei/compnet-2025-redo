"""
Topologie Mininet: Triunghi de 3 routere + 2 hosturi
  h1 conectat la r1, h3 conectat la r3
  Linkuri router-router: r1-r2, r2-r3, r1-r3

La pornire, calea activa este h1->r1->r3->h3.
r2 este izolat (nu are rute spre h1 sau h3).
Studentul va activa r2 ca ruta alternativa, apoi va elimina legatura r1-r3.
"""

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import setLogLevel


class LinuxRouter(Node):
    """Nod Mininet cu IP forwarding activat — se comporta ca un router Linux."""
    def config(self, **params):
        super(LinuxRouter, self).config(**params)
        self.cmd("sysctl -w net.ipv4.ip_forward=1")

    def terminate(self):
        super(LinuxRouter, self).terminate()


class TriangleRoutingTopo(Topo):
    """
    Topologia triunghiului r1-r2-r3, plus hosturi h1 (la r1) si h3 (la r3).

    Ordinea addLink determina numele interfetelor:
      h1-eth0  <->  r1-eth0   (h1  <-> r1)
      h3-eth0  <->  r3-eth0   (h3  <-> r3)
      r1-eth1  <->  r2-eth0   (r1  <-> r2)
      r2-eth1  <->  r3-eth1   (r2  <-> r3)
      r1-eth2  <->  r3-eth2   (r1  <-> r3)
    """
    def build(self):
        r1 = self.addNode('r1', cls=LinuxRouter)
        r2 = self.addNode('r2', cls=LinuxRouter)
        r3 = self.addNode('r3', cls=LinuxRouter)

        h1 = self.addHost('h1')
        h3 = self.addHost('h3')

        self.addLink(h1, r1)   # h1-eth0  <-> r1-eth0
        self.addLink(h3, r3)   # h3-eth0  <-> r3-eth0
        self.addLink(r1, r2)   # r1-eth1  <-> r2-eth0
        self.addLink(r2, r3)   # r2-eth1  <-> r3-eth1
        self.addLink(r1, r3)   # r1-eth2  <-> r3-eth2


def run():
    topo = TriangleRoutingTopo()
    net = Mininet(topo=topo, link=TCLink, controller=None)
    net.start()

    r1, r2, r3 = net.get('r1'), net.get('r2'), net.get('r3')
    h1, h3     = net.get('h1'), net.get('h3')

    # ------------------------------------------------------------------
    # Configurare adrese IP pe interfete
    # ------------------------------------------------------------------

    # h1 <-> r1
    h1.setIP("10.0.1.2/30",  intf="h1-eth0")
    r1.setIP("10.0.1.1/30",  intf="r1-eth0")

    # r1 <-> r2
    r1.setIP("10.0.12.1/30", intf="r1-eth1")
    r2.setIP("10.0.12.2/30", intf="r2-eth0")

    # r2 <-> r3
    r2.setIP("10.0.23.1/30", intf="r2-eth1")
    r3.setIP("10.0.23.2/30", intf="r3-eth1")

    # r1 <-> r3
    r1.setIP("10.0.13.1/30", intf="r1-eth2")
    r3.setIP("10.0.13.2/30", intf="r3-eth2")

    # r3 <-> h3
    r3.setIP("10.0.3.1/30",  intf="r3-eth0")
    h3.setIP("10.0.3.2/30",  intf="h3-eth0")

    # ------------------------------------------------------------------
    # Rute initiale — calea activa: h1 -> r1 -> r3 -> h3
    # r2 este izolat: nu are rute spre h1 sau h3
    # ------------------------------------------------------------------

    # Gateway implicit pentru hosturi
    h1.cmd("ip route add default via 10.0.1.1")
    h3.cmd("ip route add default via 10.0.3.1")

    # r1: trimite traficul spre h3 (10.0.3.0/30) direct prin r3
    r1.cmd("ip route add 10.0.3.0/30 via 10.0.13.2")

    # r3: trimite traficul spre h1 (10.0.1.0/30) direct prin r1
    r3.cmd("ip route add 10.0.1.0/30 via 10.0.13.1")

    # r2: fara rute spre h1 sau h3 — izolat intentionat

    # ------------------------------------------------------------------
    print("\n=== Topologia a fost pornita ===")
    print("Calea activa: h1 -> r1 -> r3 -> h3  (r2 este izolat)")
    print("Testati cu:   h1 ping -c 4 10.0.3.2")
    print("Urmati sarcinile din fisierul de exercitii.\n")
    # ------------------------------------------------------------------

    CLI(net)
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    run()