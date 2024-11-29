import docker
import time
import os

class NetworkMonitor:
    '''
    /proc/net/tcp or udp are files of the Linux filesystem which stores the active TCP 
    or UDP connections. These files are built in all Linux systems and this allows the 
    active connections of the container to be monitored, at the same time, without having
    the need to modify the container.

    However, the contents of the files requires to be parsed to be human-readable 
    Thus, this function serves to parse contents within those files to ensure that they
    are human-readable 
    '''
    def __init__(self, container_name):
        self.container = container_name
        self.tcp_file = "/proc/net/tcp"
        self.udp_file = "/proc/net/udp"
        self.active_connections = {}
        self.dead_connections = []
        
        self.state_map = {
            "01": "ESTABLISHED",
            "02": "SYN_SENT",
            "03": "SYN_RECV",
            "04": "FIN_WAIT1",
            "05": "FIN_WAIT2",
            "06": "TIME_WAIT",
            "07": "CLOSE",
            "08": "CLOSE_WAIT",
            "09": "LAST_ACK",
            "0A": "LISTEN",
            "0B": "CLOSING"
        }

    def convert_ip(self, hex_ip):
        if isinstance(hex_ip, str):
            hex_ip = int(hex_ip, 16)

        # Extracting the four separate octets of the IP Address
        first_octet = hex_ip & 0xFF # Bitwise operation to extract first byte or octet
        second_octet = (hex_ip >> 8) & 0xFF
        third_octet = (hex_ip >> 16) & 0xFF
        fourth_octet = (hex_ip >> 24) & 0xFF

        readable_ip_address = f"{first_octet}.{second_octet}.{third_octet}.{fourth_octet}"
        return readable_ip_address

    def convert_port(self, hex_port):
        if isinstance(hex_port, str):
            return int(hex_port, 16)

        return hex_port

    def parse_network_data(self, file):
        try:
            result = self.container.exec_run(f"cat {file}").output.decode("utf-8")
        except Exception as e:
            print(f"Error Reading File: {e}")

        lines = result.strip().split("\n")[1:] # Remove the header line
        connections = []

        for line in lines:
            fields = line.split()
            local_address, local_port = fields[1].split(":") # Separate the Local Address and Port fields
            remote_address, remote_port = fields[2].split(":") # Separate the Remote Address and Port fields
            
            local_address = self.convert_ip(int(local_address, 16))
            local_port = self.convert_port(int(local_port, 16))
            remote_address = self.convert_ip(int(remote_address, 16))
            remote_port = self.convert_port(int(remote_port, 16))

            if file == self.tcp_file:
                state_code = fields[3] # TCP States
                state = self.state_map.get(state_code, "UNKNOWN")
                
            elif file == self.udp_file:
                state = "NA" # UDP does not have states
            else:
                print("Unexpected error: Data Parsing Failed")
                break
            
            connections.append({
                "local_ip": local_address,
                "local_port": local_port,
                "remote_ip": remote_address,
                "remote_port": remote_port,
                "state": state
            })

        return connections

    def monitor_network(self):
        while True:
            os.system("clear")
            print(f"Monitoring Connections for Container {self.container.name}")
            print("=" * 50)

            current_connections = []

            for file in [self.tcp_file, self.udp_file]:

                connections = self.parse_network_data(file)
                if not connections:
                    continue

                if file == self.tcp_file:
                    print("TCP Connections: ")
                elif file == self.udp_file:
                    print("UDP Connections:")
  
                for connection in connections:
                    local_ip_port = f"{connection['local_ip']}:{connection['local_port']}"
                    remote_ip_port = f"{connection['remote_ip']}:{connection['remote_port']}"
                    state = connection['state']
                    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())  # Timestamp of the connection

                    current_connections.append(local_ip_port)
                    
                    if local_ip_port not in self.active_connections:
                        self.active_connections[local_ip_port] = {
                            'remote_ip_port': remote_ip_port,
                            'state': state,
                            'timestamp': timestamp
                        }
                        print(f"{local_ip_port} -> {remote_ip_port} (State: {state}) [New]")
                    else:
                        self.active_connections[local_ip_port].update({
                            'state': state,
                            'timestamp': timestamp
                        })
                        print(f"{local_ip_port} -> {remote_ip_port} (State: {state})")

                print("-" * 50)
            
            dead_connections = [conn for conn in self.active_connections if conn not in current_connections]

            # Log dead connections
            for dead_conn in dead_connections:
                connection = self.active_connections[dead_conn]
                self.dead_connections.append({
                    'connection': dead_conn,
                    'remote_ip_port': connection['remote_ip_port'],
                    'state': connection['state'],
                    'timestamp': connection['timestamp']
                })
            
            # Remove dead connections from active_connections
            for dead_conn in dead_connections:
                del self.active_connections[dead_conn]

            if self.dead_connections:
                print("Dead Connections (Last Seen):")
                for dead_conn in self.dead_connections:
                    print(f"Dead Connection: {dead_conn['connection']} -> {dead_conn['remote_ip_port']} "
                          f"(Last State: {dead_conn['state']}) (Last Seen: {dead_conn['timestamp']})")

            time.sleep(1)

# if __name__ == "__main__":
#     container_name = "7d47cbc3fd39"
#     monitor = NetworkMonitor(container_name)
#     monitor.monitor_network()
                