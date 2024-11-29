import time
import keyboard
import docker
import os
import subprocess
import re

from datetime import datetime
from ContainerForensics import ContainerForensics
from ContainerImager import ContainerImager

class ProcessMonitor:
    def __init__(self, selected_container):
        self.selected_container = selected_container
        self.processes = {}
        self.criticalProcesses = ["nc",
                                  "netcat",
                                  re.compile(r"bash\s+-i\s+>&\s+/dev/tcp/\d{1,3}(\.\d{1,3}){3}/\d+\s+0>&1"), # bash -i >& /dev/tcp/<IP>/<PORT> 0>&1
                                  re.compile(r"(/tmp|/dev/shm)/[^/]+$"),  # Execution from /tmp or /dev/shm
                                  re.compile(r"ssh\s+[-]([LR])\s+\S+\s+\d+"),  # SSH port forwarding (local or remote)
                                  ]

    def monitor_processes(self):
        if self.selected_container is None:
            print("No container selected for monitoring.")
            return

        container_info = self.selected_container.attrs
        entrypoint_list = container_info['Config'].get('Entrypoint', [])
        cmd_list = container_info['Config'].get('Cmd', [])
        commands = {'entrypoint': entrypoint_list, 'cmd': cmd_list}
        formatted_output = {}

        for key, value in commands.items():
            if isinstance(value, list):
                formatted_output[key] = " ".join(value)
            else:
                formatted_output[key] = value

        entrypoint = formatted_output['entrypoint']
        container_cmd = formatted_output['cmd']
        
        if entrypoint:
            combination = set([f"{entrypoint} {container_cmd}", container_cmd])
        else:
            combination = set([(container_cmd)])

        while True:            
            try:
                result = subprocess.run(
                    ['docker', 'exec', self.selected_container.id, 'ps', 'aux'],
                    capture_output=True, text=True, check=True
                )

                process_lines = result.stdout.strip().splitlines()
                header = process_lines[0].split()
                pid_index = header.index("PID")
                cmd_index = header.index("COMMAND")

                # Convert current PIDs from process_lines to a set for easy comparison
                current_pids = set(line.split()[pid_index].strip() for line in process_lines[1:])
                terminated_pids = set(self.processes.keys()) - current_pids

                for pid in terminated_pids:
                    terminated_process = self.processes.pop(pid)
                    terminated_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    if not hasattr(self, 'terminated_process'):
                        self.terminated_process = {} 

                    self.terminated_process[pid] = {**terminated_process, 'terminated_time': terminated_time}

                # Check for new processes
                for line in process_lines[1:]:
                    process_info = line.split()
                    pid = process_info[pid_index].strip()
                    cmd = " ".join(process_info[cmd_index:]).strip()
                    for critical_process in self.criticalProcesses:
                            if isinstance(critical_process, re.Pattern):  # If it's a regex
                                if critical_process.search(cmd):
                                    print(f"Malicious process of {cmd} detected, performing forensics acquisition now!")
                                    containerForensics = ContainerForensics()
                                    containerForensics.save_container_image(self.selected_container.name, "./results/output.tar")
                                    containerImager = ContainerImager()
                                    containerImager.create_disk_image("./results/output.tar", "./results/disk_image.img")
                                    exit(0)
                            else:  # If it's a direct command string
                                if critical_process in cmd:
                                        print(f"Malicious process of {cmd} detected, performing forensics acquisition now!")
                                        containerForensics = ContainerForensics()
                                        containerForensics.save_container_image(self.selected_container.name, "./results/output.tar")
                                        containerImager = ContainerImager()
                                        containerImager.create_disk_image("./results/output.tar", "./results/disk_image.img")
                                        exit(0)  # Exit the loop and stop the program

                    if not (cmd in combination or "ps aux" in cmd):
                        if pid not in self.processes:
                            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            self.processes[pid] = {'name': cmd, 'start_time': current_time}
                            break

                # Output
                os.system("clear")
                print(f"Container ID: {self.selected_container.id}")
                print(f"Container Name: {self.selected_container.name}")
                print("=" * 80)
                print("New Processes:")
                for pid, process in self.processes.items():
                    print(f"Process Name: {process['name']} (PID: {pid}, Start Time: {process['start_time']})")
                print("=" * 80)

                print("Terminated Processes:")
                if hasattr(self, 'terminated_process') and self.terminated_process:
                    for pid, process in self.terminated_process.items():
                        print(f"Process Name: {process['name']} (PID: {pid}, Terminated Time: {process['terminated_time']})")

                print("=" * 80)
                time.sleep(1)

            except subprocess.CalledProcessError as error:
                print(f"An error has occurred: {error}")
            except Exception as e:
                print(f"Unexpected error: {e}")

# if __name__ == "__main__":
#     container_name = "7d47cbc3fd39"
#     client = docker.from_env()
#     container = client.containers.get(container_name)
#     monitor = ContainerMonitor(container,client)
#     monitor.monitor_processes()

