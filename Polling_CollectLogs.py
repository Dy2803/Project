# polling_controller.py – Đo băng thông theo thời gian thực và ghi vào polling_raw.csv
import csv, os, time
from datetime import datetime
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib import hub
from ryu.lib.packet import packet, ethernet
from ryu.lib.packet import ether_types

class PollingController(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.datapaths = {}
        self.csv_file = 'polling_raw.csv'
        self.interval = 1
        self.start_time = 0
        self._prepare_csv()
        self.monitor_thread = hub.spawn(self._monitor)

    def _prepare_csv(self):
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, 'w', newline='') as f:
                csv.writer(f).writerow(['real_time', 'elapsed', 'dpid', 'eth_src', 'eth_dst', 'byte_count', 'duration_sec'])

    @set_ev_cls(ofp_event.EventOFPStateChange, [CONFIG_DISPATCHER, MAIN_DISPATCHER])
    def _state_change_handler(self, ev):
        dp = ev.datapath
        if ev.state == MAIN_DISPATCHER:
            self.datapaths[dp.id] = dp
            self._install_table_miss(dp)
        elif ev.state != MAIN_DISPATCHER and dp.id in self.datapaths:
            del self.datapaths[dp.id]

    def _install_table_miss(self, dp):
        parser = dp.ofproto_parser
        ofproto = dp.ofproto
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER)]
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(datapath=dp, priority=0, match=match, instructions=inst)
        dp.send_msg(mod)

    def _monitor(self):
        while True:
            for dp in self.datapaths.values():
                if dp.id == 2:
                    self._request_flow_stats(dp)
            hub.sleep(self.interval)

    def _request_flow_stats(self, datapath):
        parser = datapath.ofproto_parser
        req = parser.OFPFlowStatsRequest(datapath)
        datapath.send_msg(req)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        dp = msg.datapath
        parser = dp.ofproto_parser
        ofproto = dp.ofproto
        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)
        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            return

        if self.start_time == 0:
            self.start_time = time.time()

        in_port = msg.match['in_port']
        actions = [parser.OFPActionOutput(ofproto.OFPP_FLOOD)]
        match = parser.OFPMatch(in_port=in_port, eth_src=eth.src, eth_dst=eth.dst)
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(
            datapath=dp,
            priority=1,
            match=match,
            instructions=inst,
            idle_timeout=30,
            flags=ofproto.OFPFF_SEND_FLOW_REM
        )
        dp.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
    def _flow_stats_reply_handler(self, ev):
        dpid = ev.msg.datapath.id
        now = time.time()
        elapsed = now - self.start_time if self.start_time > 0 else 0
        flow_table = []

        for stat in ev.msg.body:
            if stat.priority == 0 or stat.packet_count == 0:
                continue

            match = dict(stat.match.items())
            eth_src = match.get('eth_src', '')
            eth_dst = match.get('eth_dst', '')
            byte_count = stat.byte_count
            duration_sec = stat.duration_sec

            with open(self.csv_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    f"{elapsed:.2f}",  # ghi elapsed ở cả real_time và elapsed
                    f"{elapsed:.2f}",
                    dpid,
                    eth_src,
                    eth_dst,
                    byte_count,
                    duration_sec
                ])

            flow_table.append((eth_src, eth_dst, byte_count, duration_sec))

        ts = datetime.fromtimestamp(now).strftime('%Y-%m-%d %H:%M:%S')
        if flow_table:
            print(f"\n[FlowStats Table] @ {ts} (elapsed = {elapsed:.2f}s, dpid={dpid}):")
            print("{:<20} {:<20} {:>10} {:>12}".format("eth_src", "eth_dst", "bytes", "duration"))
            print("-" * 66)
            for src, dst, bytes_, dur in flow_table:
                print(f"{src:<20} {dst:<20} {bytes_:>10} {dur:>10.2f}s")
        else:
            print(f"[FlowStats Table] @ {ts} (elapsed = {elapsed:.2f}s, dpid={dpid}) → No active flows.")
