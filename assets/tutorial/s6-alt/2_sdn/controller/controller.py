"""
Controller OS-Ken simplu pentru topologia:
    h1 ---- s1 ---- h2
             |
            h3

Comportament:
 - Traficul intre h1 (10.0.10.1) si h2 (10.0.10.2) este permis (flow-uri instalate).
 - Traficul catre h3 (10.0.10.3) este blocat (flow de tip drop).

-------------------------------------------------------------------------------
CONCEPTE DE BAZA — cititi inainte de a studia codul
-------------------------------------------------------------------------------

Un controller SDN primeste pachete de la switch prin evenimente "PacketIn".
Acestea apar doar pentru pachetele pe care switch-ul NU stie cum sa le trateze
(nu exista un flow potrivit in tabela lui).

Controllerul poate raspunde in doua moduri:
  1. PacketOut  — trimite pachetul curent pe un port anume (o singura data)
  2. FlowMod    — instaleaza o regula (flow) in switch, astfel incat pachetele
                  viitoare cu acelasi pattern sa fie tratate direct de switch,
                  fara sa mai ajunga la controller

Un flow are doua parti:
  - match  : conditia (ex: "pachetele IPv4 cu dst=10.0.10.2")
  - actions: ce se face (ex: "trimite pe portul 2" sau "" = drop)

Prioritatea unui flow determina care regula castiga daca mai multe se potrivesc.
O prioritate mai mare castiga. Prioritatea 0 este regula implicita (table-miss).
"""

from os_ken.base import app_manager
from os_ken.controller import ofp_event
from os_ken.controller.handler import MAIN_DISPATCHER, CONFIG_DISPATCHER, set_ev_cls
from os_ken.ofproto import ofproto_v1_3
from os_ken.lib.packet import packet, ethernet, ipv4, arp


class SimpleSwitch13(app_manager.OSKenApp):
    # Specificam ca folosim OpenFlow 1.3
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    # MAC-urile sunt atribuite automat de Mininet (autoSetMacs=True):
    # primul host primeste ...01, al doilea ...02, etc.
    H1_MAC = "00:00:00:00:00:01"
    H2_MAC = "00:00:00:00:00:02"
    H3_MAC = "00:00:00:00:00:03"

    def __init__(self, *args, **kwargs):
        super(SimpleSwitch13, self).__init__(*args, **kwargs)
        # Tabel de invatare L2: retinem pe ce port am vazut fiecare MAC
        # Structura: { dpid_switch -> { mac -> port } }
        self.mac_to_port = {}

    # ------------------------------------------------------------------
    # EVENT 1: switch-ul s-a conectat la controller
    # ------------------------------------------------------------------
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        """
        Apelat automat cand un switch OpenFlow se conecteaza la controller.

        Instalam regula "table-miss" cu prioritatea 0 (cea mai mica):
          match  : orice pachet (fara conditii)
          actions: trimite pachetul la controller (OFPP_CONTROLLER)

        Fara aceasta regula, switch-ul ar arunca pachetele necunoscute
        in loc sa le trimita la controller.
        """
        datapath = ev.msg.datapath       # referinta catre switch
        ofproto  = datapath.ofproto      # constantele protocolului OpenFlow
        parser   = datapath.ofproto_parser  # constructori pentru mesaje OF

        # match gol = se potriveste cu orice pachet
        match = parser.OFPMatch()

        # actiunea: trimite la controller, fara a pune pachetul in buffer
        actions = [parser.OFPActionOutput(
            ofproto.OFPP_CONTROLLER,
            ofproto.OFPCML_NO_BUFFER
        )]

        self.add_flow(datapath, priority=0, match=match, actions=actions)
        self.logger.info("Table-miss flow instalat pe switch %s", datapath.id)

    # ------------------------------------------------------------------
    # HELPER: instaleaza un flow in switch
    # ------------------------------------------------------------------
    def add_flow(self, datapath, priority, match, actions, buffer_id=None):
        """
        Trimite un mesaj FlowMod catre switch pentru a instala o regula noua.

        Parametri:
          datapath  : switch-ul tinta
          priority  : prioritatea regulii (mai mare = mai importanta)
          match     : conditia de potrivire (pe ce pachete se aplica)
          actions   : ce se face cu pachetul (lista; goala = drop)
          buffer_id : daca pachetul curent e in bufferul switch-ului,
                      il putem referentia direct pentru a evita retransmisia
        """
        ofproto = datapath.ofproto
        parser  = datapath.ofproto_parser

        # OFPIT_APPLY_ACTIONS = aplica actiunile imediat (nu le pune in queue)
        inst = [parser.OFPInstructionActions(
            ofproto.OFPIT_APPLY_ACTIONS,
            actions
        )]

        # Construim mesajul FlowMod (cu sau fara buffer_id)
        if buffer_id is not None and buffer_id != ofproto.OFP_NO_BUFFER:
            mod = parser.OFPFlowMod(
                datapath=datapath,
                buffer_id=buffer_id,
                priority=priority,
                match=match,
                instructions=inst
            )
        else:
            mod = parser.OFPFlowMod(
                datapath=datapath,
                priority=priority,
                match=match,
                instructions=inst
            )

        datapath.send_msg(mod)

    # ------------------------------------------------------------------
    # EVENT 2: switch-ul a primit un pachet fara flow potrivit
    # ------------------------------------------------------------------
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        """
        Apelat cand switch-ul trimite un pachet necunoscut la controller
        (a fost prins de regula table-miss).

        Logica:
          - Pachete ARP: tratate simplu ca un L2 learning switch
                         (invatam portul sursei, trimitem catre destinatie
                          sau flood daca nu o stim inca)
          - Pachete IPv4: aplicam politica SDN
                          * h1 <-> h2 : permis, instalam flow bidiectional
                          * orice -> h3 : blocat, instalam flow drop
        """
        msg      = ev.msg
        datapath = msg.datapath
        dpid     = datapath.id
        ofproto  = datapath.ofproto
        parser   = datapath.ofproto_parser

        # Portul fizic pe care a intrat pachetul in switch
        in_port = msg.match['in_port']

        # Despachetam layerele din pachet
        pkt      = packet.Packet(data=msg.data)
        eth      = pkt.get_protocols(ethernet.ethernet)[0]  # header Ethernet (intotdeauna prezent)
        ipv4_pkt = pkt.get_protocol(ipv4.ipv4)              # header IPv4 (None daca nu e IP)
        arp_pkt  = pkt.get_protocol(arp.arp)                # header ARP (None daca nu e ARP)

        src_mac = eth.src
        dst_mac = eth.dst

        # ------------------------------------------------------------
        # L2 Learning: retinem pe ce port am vazut adresa MAC sursa.
        # Astfel, data viitoare stim direct pe ce port sa trimitem
        # pachetele destinate acestui MAC.
        # ------------------------------------------------------------
        self.mac_to_port.setdefault(dpid, {})
        self.mac_to_port[dpid][src_mac] = in_port

        self.logger.info("PacketIn: dpid=%s eth_src=%s eth_dst=%s in_port=%s",
                         dpid, src_mac, dst_mac, in_port)

        # ============================================================
        # CAZ 1: pachet ARP
        # ARP este folosit pentru a descoperi MAC-ul unui IP vecin.
        # Nu aplicam politica SDN pe ARP — il tratam ca un switch L2 simplu.
        # ============================================================
        if arp_pkt:
            self.logger.info("ARP: %s -> %s (op=%s)",
                             arp_pkt.src_ip, arp_pkt.dst_ip, arp_pkt.opcode)

            # Daca stim deja portul destinatarului, trimitem direct.
            # Altfel, flood pe toate porturile (exceptand cel de intrare).
            if dst_mac in self.mac_to_port[dpid]:
                out_port = self.mac_to_port[dpid][dst_mac]
            else:
                out_port = ofproto.OFPP_FLOOD  # trimite pe toate porturile

            actions = [parser.OFPActionOutput(out_port)]

            # Trimitem pachetul ARP curent cu PacketOut (fara a instala flow)
            out = parser.OFPPacketOut(
                datapath=datapath,
                buffer_id=ofproto.OFP_NO_BUFFER,
                in_port=in_port,
                actions=actions,
                data=msg.data
            )
            datapath.send_msg(out)
            return  # gata cu ARP, nu mai procesam

        # ============================================================
        # CAZ 2: alt protocol (non-IPv4, non-ARP) — ignoram
        # ============================================================
        if not ipv4_pkt:
            return

        src_ip = ipv4_pkt.src
        dst_ip = ipv4_pkt.dst

        self.logger.info("IPv4: %s -> %s", src_ip, dst_ip)

        # ============================================================
        # POLITICA SDN — CAZ A: trafic intre h1 si h2 => PERMIS
        # Instalam un flow cu prioritatea 10 care va trata direct
        # pachetele viitoare cu acelasi src/dst IP, fara sa mai
        # fie nevoie sa ajunga la controller.
        # ============================================================
        if ((src_ip == "10.0.10.1" and dst_ip == "10.0.10.2") or
                (src_ip == "10.0.10.2" and dst_ip == "10.0.10.1")):

            # Determinam portul de iesire pe baza MAC-ului sursa/destinatie.
            # Porturile fizice in Mininet: h1=port1, h2=port2, h3=port3
            out_port = None
            if src_mac == self.H1_MAC and dst_mac == self.H2_MAC:
                out_port = 2   # h1 -> h2: iesim pe portul 2
            elif src_mac == self.H2_MAC and dst_mac == self.H1_MAC:
                out_port = 1   # h2 -> h1: iesim pe portul 1

            if out_port is None:
                # Fallback: cautam in tabelul de invatare L2
                out_port = self.mac_to_port[dpid].get(
                    dst_mac,
                    ofproto.OFPP_FLOOD
                )

            actions = [parser.OFPActionOutput(out_port)]

            # match: pachete IPv4 cu exact acest src si dst IP
            match = parser.OFPMatch(
                eth_type=0x0800,   # 0x0800 = IPv4
                ipv4_src=src_ip,
                ipv4_dst=dst_ip
            )

            # Instalam flow-ul (pachetele viitoare nu mai vin la controller)
            self.add_flow(
                datapath,
                priority=10,
                match=match,
                actions=actions,
                buffer_id=msg.buffer_id if msg.buffer_id != ofproto.OFP_NO_BUFFER else None
            )

            # Daca pachetul curent nu e in buffer, il trimitem si pe el acum
            if msg.buffer_id == ofproto.OFP_NO_BUFFER:
                out = parser.OFPPacketOut(
                    datapath=datapath,
                    buffer_id=ofproto.OFP_NO_BUFFER,
                    in_port=in_port,
                    actions=actions,
                    data=msg.data
                )
                datapath.send_msg(out)

            self.logger.info("Permis: %s -> %s prin portul %s", src_ip, dst_ip, out_port)
            return

        # ============================================================
        # POLITICA SDN — CAZ B: destinatia este h3 => BLOCAT (drop)
        # Instalam un flow cu prioritatea 20 si actions=[] (lista goala).
        # O lista goala de actiuni inseamna drop — pachetul este aruncat.
        # Prioritatea 20 > 10, deci acest flow castiga fata de orice
        # regula de permitere care ar putea exista pentru acelasi pachet.
        # ============================================================
        if dst_ip == "10.0.10.3":
            match = parser.OFPMatch(
                eth_type=0x0800,
                ipv4_dst=dst_ip   # match doar pe destinatie, indiferent de sursa
            )
            actions = []  # lista goala = drop (nicio actiune = pachetul dispare)

            self.add_flow(
                datapath,
                priority=20,
                match=match,
                actions=actions,
                buffer_id=msg.buffer_id if msg.buffer_id != ofproto.OFP_NO_BUFFER else None
            )

            self.logger.info("Blocat: trafic catre %s (flow drop instalat)", dst_ip)
            # Nu trimitem PacketOut — pachetul curent este si el dropp-uit.
            return

        # ============================================================
        # CAZ IMPLICIT: niciun caz de mai sus nu s-a potrivit
        # Logam si ignoram — pachetul este aruncat implicit.
        # ============================================================
        self.logger.info("Trafic neacoperit explicit: %s -> %s (ignorat)", src_ip, dst_ip)