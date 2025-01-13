#!/usr/bin/env python3
import psutil
import time
import curses
import datetime
import sys
from collections import deque
from scapy.all import sniff, IP, TCP, UDP
import threading
import queue
import ipaddress
from typing import Optional, Dict, List

class Panel:
    def __init__(self, window, y, x, height, width, title=""):
        self.window = curses.newwin(height, width, y, x)
        self.window.box()
        self.height = height
        self.width = width
        self.title = title
        if title:
            self.window.addstr(0, 2, f" {title} ")
        self.window.refresh()

    def clear_content(self):
        for y in range(1, self.height-1):
            self.window.addstr(y, 1, " " * (self.width-2))

    def add_line(self, y, x, text, color_pair=0):
        try:
            if 0 <= y < self.height-1 and 0 <= x < self.width-1:
                max_len = self.width - x - 2
                if max_len > 0:
                    self.window.addstr(y+1, x+1, text[:max_len], color_pair)
        except curses.error:
            pass

    def refresh(self):
        self.window.refresh()

class PacketLog:
    def __init__(self, maxsize=100):
        self.logs = deque(maxlen=maxsize)
        self.packet_queue = queue.Queue()
        self.packet_counts: Dict[str, int] = {}
        self.protocol_counts: Dict[str, int] = {}
        self.active_connections: Dict[str, Dict] = {}

    def add_packet(self, packet):
        if IP in packet:
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            src_ip = packet[IP].src
            dst_ip = packet[IP].dst
            protocol = "TCP" if TCP in packet else "UDP" if UDP in packet else "Other"

            # port info
            src_port = dst_port = "?"
            if TCP in packet:
                src_port = packet[TCP].sport
                dst_port = packet[TCP].dport
            elif UDP in packet:
                src_port = packet[UDP].sport
                dst_port = packet[UDP].dport

            log_entry = f"{timestamp} {protocol:5} {src_ip}:{src_port} → {dst_ip}:{dst_port}"
            self.packet_queue.put(log_entry)

            # update stats
            self.packet_counts[src_ip] = self.packet_counts.get(src_ip, 0) + 1
            self.protocol_counts[protocol] = self.protocol_counts.get(protocol, 0) + 1

            # track active connections
            conn_key = f"{src_ip}:{src_port}-{dst_ip}:{dst_port}"
            self.active_connections[conn_key] = {
                "protocol": protocol,
                "last_seen": timestamp,
                "bytes": len(packet)
            }

class NetworkMonitor:
    def __init__(self, window):
        self.main_window = window
        curses.start_color()
        curses.use_default_colors()
        
        # color pairs
        curses.init_pair(1, curses.COLOR_GREEN, -1)
        curses.init_pair(2, curses.COLOR_YELLOW, -1)
        curses.init_pair(3, curses.COLOR_RED, -1)
        curses.init_pair(4, curses.COLOR_CYAN, -1)
        curses.init_pair(5, curses.COLOR_MAGENTA, -1)

        # initialize stats
        self.upload_history = deque([0] * 30, maxlen=30)
        self.download_history = deque([0] * 30, maxlen=30)
        self.packet_log = PacketLog()

        self.net_io = psutil.net_io_counters()
        self.last_upload = self.net_io.bytes_sent
        self.last_download = self.net_io.bytes_recv
        self.last_time = time.time()

        # packet capture in separate thread
        self.capture_thread = threading.Thread(target=self.capture_packets, daemon=True)
        self.running = True

    def capture_packets(self):
        try:
            sniff(prn=self.packet_log.add_packet, store=0)
        except Exception as e:
            self.packet_log.packet_queue.put(f"Error in packet capture: {str(e)}")

    def draw_bandwidth_graph(self, panel, data, max_value, title, y_offset=0):
        if max_value == 0:
            max_value = 1
        available_width = panel.width - 4
        graph_width = min(available_width, len(data))

        panel.add_line(y_offset, 0, f"{title}: ", curses.color_pair(4))
        for i, value in enumerate(list(data)[-graph_width:]):
            height = int((value / max_value) * 8)
            char = "█" if height > 0 else "."
            panel.add_line(y_offset, i + len(title) + 2, char, curses.color_pair(1))

    def create_layout(self):
        height, width = self.main_window.getmaxyx()
        self.stats_panel = Panel(self.main_window, 0, 0, 8, width, "Network Statistics")
        self.bandwidth_panel = Panel(self.main_window, 8, 0, 5, width, "Bandwidth Graphs")
        self.packet_panel = Panel(self.main_window, 13, 0, height-13, width, "Packet Log")

    def update_stats_panel(self):
        self.stats_panel.clear_content()
        y = 0

        # ni info
        for interface, stats in psutil.net_if_stats().items():
            status = "UP" if stats.isup else "DOWN"
            color = curses.color_pair(1) if stats.isup else curses.color_pair(2)
            self.stats_panel.add_line(y, 0, f"Interface: {interface} - Status: {status}", color)
            y += 1

        # protocol stats
        protocols = self.packet_log.protocol_counts
        if protocols:
            stats_str = "Protocols: " + " ".join(f"{k}:{v}" for k, v in protocols.items())
            self.stats_panel.add_line(y, 0, stats_str, curses.color_pair(5))

        self.stats_panel.refresh()

    def update_bandwidth_panel(self):
        self.bandwidth_panel.clear_content()

        max_upload = max(self.upload_history) if self.upload_history else 1
        max_download = max(self.download_history) if self.download_history else 1

        self.draw_bandwidth_graph(self.bandwidth_panel, self.upload_history, max_upload, "Upload", 0)
        self.draw_bandwidth_graph(self.bandwidth_panel, self.download_history, max_download, "Download", 1)

        self.bandwidth_panel.refresh()

    def update_packet_panel(self):
        self.packet_panel.clear_content()

        # new packets
        while not self.packet_log.packet_queue.empty():
            try:
                log_entry = self.packet_log.packet_queue.get_nowait()
                self.packet_log.logs.append(log_entry)
            except queue.Empty:
                break

        # show packet logs
        for i, log in enumerate(list(self.packet_log.logs)[-self.packet_panel.height+2:]):
            self.packet_panel.add_line(i, 0, log, curses.color_pair(4))

        self.packet_panel.refresh()

    def run(self):
        try:
            self.create_layout()
            self.capture_thread.start()

            while self.running:
                try:
                    # get current network stats
                    net_io = psutil.net_io_counters()
                    current_time = time.time()
                    time_elapsed = current_time - self.last_time

                    if time_elapsed > 0:
                        upload_speed = (net_io.bytes_sent - self.last_upload) / time_elapsed
                        download_speed = (net_io.bytes_recv - self.last_download) / time_elapsed

                        self.upload_history.append(upload_speed)
                        self.download_history.append(download_speed)

                        self.last_upload = net_io.bytes_sent
                        self.last_download = net_io.bytes_recv
                        self.last_time = current_time

                    # update all panels
                    self.update_stats_panel()
                    self.update_bandwidth_panel()
                    self.update_packet_panel()

                    # check for quit
                    if self.main_window.getch() == ord('q'):
                        break

                    time.sleep(0.1)

                except curses.error:
                    self.main_window.clear()
                    self.main_window.addstr(0, 0, "Terminal too small. Please resize.", curses.color_pair(3))
                    self.main_window.refresh()
                    time.sleep(1)
                    self.create_layout()

        except KeyboardInterrupt:
            pass
        finally:
            self.running = False

def main():
    if not sys.platform.startswith('linux'):
        print("Warning: Packet capture requires root/sudo privileges on non-Linux systems")

    try:
        curses.wrapper(lambda stdscr: NetworkMonitor(stdscr).run())
    except Exception as e:
        print(f"Fatal error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()