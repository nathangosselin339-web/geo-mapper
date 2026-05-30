import socket
import threading
import json
import sys
from typing import Callable, Optional

class MinecraftListener:
    def __init__(self, on_place: Callable, on_command: Optional[Callable] = None, host: str = "127.0.0.1", port: int = 19528):
        self.host = host
        self.port = port
        self.on_place = on_place
        self.on_command = on_command
        self.server = None
        self.running = False
        self.origin_x = 0
        self.origin_z = 0

    def set_origin(self, ox: int, oz: int):
        self.origin_x = ox
        self.origin_z = oz

    def start_tcp_server(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.host, self.port))
        self.server.listen(1)
        self.server.settimeout(1.0)
        self.running = True
        thread = threading.Thread(target=self._tcp_loop, daemon=True)
        thread.start()

    def _tcp_loop(self):
        while self.running:
            try:
                conn, addr = self.server.accept()
                with conn:
                    data = conn.recv(4096)
                    if data:
                        msg = json.loads(data.decode("utf-8"))
                        self._handle_message(msg)
            except socket.timeout:
                continue
            except Exception as e:
                print(f"[TCP] Error: {e}")

    def _handle_message(self, msg: dict):
        if msg.get("type") == "block_place":
            wx = msg.get("x", 0)
            wz = msg.get("z", 0)
            block_id = msg.get("block", "minecraft:stone")
            self.on_place(wx, wz, block_id)

    def start_manual_input(self):
        print("Manual input mode. Enter: x z block_id")
        print(f"Origin set to ({self.origin_x}, {self.origin_z})")
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            if line.lower() in ("exit", "quit"):
                break
            if line.lower().startswith("origin"):
                parts = line.split()
                if len(parts) >= 3:
                    self.origin_x = int(parts[1])
                    self.origin_z = int(parts[2])
                    print(f"Origin set to ({self.origin_x}, {self.origin_z})")
                continue
            if line.lower() in ("reset", "stats"):
                if self.on_command:
                    self.on_command(line.lower())
                continue
            parts = line.split()
            if len(parts) >= 3:
                wx = int(parts[0])
                wz = int(parts[1])
                block_id = parts[2]
                self.on_place(wx + self.origin_x, wz + self.origin_z, block_id)

    def stop(self):
        self.running = False
        if self.server:
            self.server.close()
