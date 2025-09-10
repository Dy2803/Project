from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.link import TCLink
from mininet.cli import CLI
from time import sleep, time

class FlowSensePAM13Topo(Topo):
    def build(self):
        s1 = self.addSwitch('s1')  # Switch A
        s2 = self.addSwitch('s2')  # Switch B
        h1 = self.addHost('h1', mac='00:00:00:00:00:01', ip='10.0.0.1/24')
        h2 = self.addHost('h2', mac='00:00:00:00:00:02', ip='10.0.0.2/24')
        h3 = self.addHost('h3', mac='00:00:00:00:00:03', ip='10.0.0.3/24')

        self.addLink(h1, s1)
        self.addLink(s1, s2)
        self.addLink(h2, s2)
        self.addLink(h3, s2)

if __name__ == '__main__':
    topo = FlowSensePAM13Topo()
    net = Mininet(
        topo=topo,
        controller=lambda name: RemoteController(name, ip='127.0.0.1', port=6653),
        link=TCLink
    )
    net.start()

    h1, h2, h3 = net.get('h1', 'h2', 'h3')

    # Thiết lập lại địa chỉ MAC/IP nếu cần (phòng khi Mininet override)
    h1.setMAC('00:00:00:00:00:01')
    h1.setIP('10.0.0.1/24')
    h2.setMAC('00:00:00:00:00:02')
    h2.setIP('10.0.0.2/24')
    h3.setMAC('00:00:00:00:00:03')
    h3.setIP('10.0.0.3/24')

    print("[INFO] Starting iperf UDP server on h2 (hostB1)")
    h2.cmd('iperf -s -u -p 5001 &')
    print("[INFO] Starting iperf UDP server on h3 (hostB2)")
    h3.cmd('iperf -s -u -p 5002 &')
    sleep(2)

    start = time()
    print("[INFO] Starting background 10 Mbps flow to h3 for 180s")
    h1.cmd(f'iperf -c {h3.IP()} -u -b 10M -t 180 -p 5002 &')

    print(f"[PHASE 1] t = {int(time()-start)}s → h1 → h2 at 20 Mbps for 20s")
    h1.cmd(f'iperf -c {h2.IP()} -u -b 20M -t 20 -p 5001')
    sleep(2)

    sleep(20)
    print(f"[PHASE 2] t = {int(time()-start)}s → h1 → h2 at 45 Mbps for 30s")
    h1.cmd(f'iperf -c {h2.IP()} -u -b 45M -t 30 -p 5001')
    sleep(2)

    sleep(30)
    print(f"[PHASE 3] t = {int(time()-start)}s → h1 → h2 at 30 Mbps for 20s")
    h1.cmd(f'iperf -c {h2.IP()} -u -b 30M -t 20 -p 5001')

    print("[INFO] Traffic done. You can run CLI or exit.")
    CLI(net)
    net.stop()
