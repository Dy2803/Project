import csv, os, time, hashlib
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet
from ryu.lib.packet import ether_types

LOG_FILE = 'flowsense_events.csv'  # nếu khảo sát granularity thì thay bằng file granularity_events.csv

def generate_flow_id(in_port, eth_src, eth_dst):
    key = f"{in_port}-{eth_src}-{eth_dst}".encode()
    return hashlib.md5(key).hexdigest()[:12]  # rút gọn cho gọn file

class FlowSenseCollector(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_time = None
        if not os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    "timestamp", "event", "dpid", "in_port", "eth_src", "eth_dst",
                    "byte_count", "duration", "idle_timeout", "flow_id"
                ])
        self.logger.info("[INIT] FlowSense Collector with flow_id ready.")

    def _log_event(self, row):
        with open(LOG_FILE, 'a', newline='') as f:
            csv.writer(f).writerow(row)

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        parser = datapath.ofproto_parser
        ofproto = datapath.ofproto
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER)]
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(datapath=datapath, priority=0, match=match, instructions=inst)
        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        parser = datapath.ofproto_parser
        ofproto = datapath.ofproto

        dpid = datapath.id
        in_port = msg.match['in_port']
        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)
        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            return

        timestamp = time.time()
        if self.start_time is None:
            self.start_time = timestamp
        elapsed = timestamp - self.start_time

        flow_id = generate_flow_id(in_port, eth.src, eth.dst)

        self._log_event([
            f"{elapsed:.6f}", "PacketIn", dpid, in_port, eth.src, eth.dst,
            "", "", "", flow_id
        ])
        self.logger.info(f"[PacketIn] dpid={dpid}, in_port={in_port}, src={eth.src}, dst={eth.dst}, flow_id={flow_id}")

        match = parser.OFPMatch(in_port=in_port, eth_src=eth.src, eth_dst=eth.dst)
        actions = [parser.OFPActionOutput(ofproto.OFPP_FLOOD)]
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(
            datapath=datapath,
            priority=1,
            match=match,
            instructions=inst,
            idle_timeout=3,
            flags=ofproto.OFPFF_SEND_FLOW_REM,
            cookie=in_port  
        )
        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPFlowRemoved, MAIN_DISPATCHER)
    def flow_removed_handler(self, ev):
        msg = ev.msg
        dpid = msg.datapath.id

        # Dù field có bị thiếu thì vẫn lấy được in_port từ cookie
        in_port = msg.cookie
        eth_src, eth_dst = "", ""

        for field in msg.match.fields:
            if field.header == 3:
                eth_src = field.value
            elif field.header == 4:
                eth_dst = field.value

        timestamp = time.time()
        if self.start_time is None:
            return
        elapsed = timestamp - self.start_time

        flow_id = generate_flow_id(in_port, eth_src, eth_dst)

        self._log_event([
            f"{elapsed:.6f}", "FlowRemoved", dpid, in_port, eth_src, eth_dst,
            msg.byte_count, msg.duration_sec, msg.idle_timeout, flow_id
        ])
        self.logger.info(f"[FlowRemoved] dpid={dpid}, in_port={in_port}, flow_id={flow_id}, bytes={msg.byte_count}, duration={msg.duration_sec}s")
