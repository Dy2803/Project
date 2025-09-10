# granularity_topo_mixed.py – Tạo nhiều flow ngắn và dài xen kẽ
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.link import TCLink
from mininet.cli import CLI
from time import sleep
import random

class FlowSenseGranularityTopo(Topo):
    def build(self):
        s1 = self.addSwitch('s1')
        for i in range(1, 13):
            h = self.addHost(f'h{i}')
            self.addLink(h, s1)

if __name__ == '__main__':
    topo = FlowSenseGranularityTopo()
    net = Mininet(topo=topo,
                  controller=lambda name: RemoteController(name, ip='127.0.0.1', port=6653),
                  link=TCLink)
    net.start()

    hlist = [net.get(f'h{i}') for i in range(1, 13)]
    for i in range(6, 12):
        hlist[i].cmd(f'iperf -s -u -p 500{i} &')
    sleep(2)

    rounds = 5
    for r in range(rounds):
        print(f"\n[ROUND {r+1}] Start flows...\n")
        for i in range(6):
            for j in range(6):
                src = hlist[i]
                dst = hlist[j+6]

                # Flow dài (ít hơn)
                if r % 2 == 0:
                    dur = random.choice([40, 60])
                else:
                    dur = random.choice([5, 8, 10])

                rate = random.choice(['5M','8M','10M'])
                delay = random.uniform(0,1)
                port = 500 + j

                src.cmd(f'sleep {delay}; iperf -c {dst.IP()} -u -b {rate} -t {dur} -p {port} &')

        sleep(25)  # Ngắn hơn để flow overlap
    print("\n[INFO] Waiting flows to finish...")
    sleep(60)
    CLI(net)
    net.stop()
