import docker
import time
import os
import subprocess
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from ContainerForensics import ContainerForensics
from ContainerImager import ContainerImager

class FileChangesMonitor:
    '''
    Command: docker inspect <container_id> | grep UpperDir
    '''
    def __init__(self, container):
        self.container = container
        self.containerID = self.container.id
        self.containerName = self.container.name

    def locate_upper_layer(self):        
        try:
            layer_result = subprocess.run(
                f"docker inspect {self.containerID} | grep MergedDir",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            if layer_result.returncode == 0:
                upper_dir = layer_result.stdout.strip().split(':')[-1].strip().strip('",')
                return upper_dir
            else:
                raise Exception(f"Error locating the UpperDir Layer of the container {result.stderr}")

        except Exception as e:
            print(f"An error has occurred {e}")
            return None
                
    def monitor_filechanges(self):
        upper_layer = self.locate_upper_layer()
        
        if upper_layer:
            os.system('clear')
            print("=" * 80)
            print(f"Monitoring File Changes in {self.containerID} ({self.containerName})")

            observer = Observer()
            event_handler = FileMonitoringHandler(observer, self.container)
            observer.schedule(event_handler, upper_layer, recursive=True)
            observer.start()

            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                observer.stop()
            
            observer.join()
        else:
            print("Unable to locate the layer of the container")
        
class FileMonitoringHandler(FileSystemEventHandler):
    def __init__(self, observer, container):
        self.timestamps = {}
        self.created_files = {}
        self.criticalFiles = ["/etc/passwd", "/etc/shadow", "/etc/hosts", "/etc/resolv.conf", "/etc/hostname", "/etc/ld.so.preload"]
        self.observer = observer
        self.container = container
        self.containerID = self.container.id
        self.containerName = self.container.name


    def get_file_path(self, filepath):
        return filepath.split('/merged/', 1)[-1]

    def log_with_timestamp(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")

    def on_modified(self, event):
        if not event.is_directory:
            current_timestamp = os.path.getmtime(event.src_path)

            if event.src_path in self.created_files:
                creation_time = self.created_files[event.src_path]
                if current_timestamp == creation_time:
                    return

            if os.path.getsize(event.src_path) > 0:
                filepath = "/" + self.get_file_path(event.src_path)
                if event.src_path in self.timestamps:
                    previous_timestamp = self.timestamps[event.src_path]
                    if current_timestamp != previous_timestamp:
                        self.timestamps[event.src_path] = current_timestamp
                        self.log_with_timestamp(f"File {filepath} has been modified.")
                        if (filepath in self.criticalFiles):
                            print(f"Malicious attempt on {filepath} made, performing forensics acquisition now!")
                            containerForensics = ContainerForensics()
                            containerForensics.save_container_image(self.containerName, "./results/output.tar")
                            containerImager = ContainerImager()
                            containerImager.create_disk_image("./results/output.tar", "./results/disk_image.img")
                            self.observer.stop()
                            exit(0)
                            # self.observer.join()
                            
                            

                else:
                    self.timestamps[event.src_path] = current_timestamp
                    self.log_with_timestamp(f"File {filepath} has been modified.")
                    if (filepath in self.criticalFiles):
                        print(f"Malicious attempt on {filepath} made, performing forensics acquisition now!")
                        containerForensics = ContainerForensics()
                        containerForensics.save_container_image(self.containerName, "./results/output.tar")
                        containerImager = ContainerImager()
                        containerImager.create_disk_image("./results/output.tar", "./results/disk_image.img")
                        self.observer.stop()
                        exit(0)
                        # self.observer.join()
                            
                              
    def on_created(self, event):
        if not event.is_directory:
            time.sleep(0.5)
            filepath = "/" + self.get_file_path(event.src_path)

            if os.path.exists(event.src_path) and os.path.getsize(event.src_path) > 0:
                self.created_files[event.src_path] = os.path.getmtime(event.src_path)    
                self.log_with_timestamp(f"File {filepath} has been created with contents.")
                if (filepath in self.criticalFiles):
                    print(f"Malicious attempt on {filepath} made, performing forensics acquisition now!")
                    containerForensics = ContainerForensics()
                    containerForensics.save_container_image(self.containerName, "./results/output.tar")
                    containerImager = ContainerImager()
                    containerImager.create_disk_image("./results/output.tar", "./results/disk_image.img")
                    self.observer.stop()
                    exit(0)
                    # self.observer.join()
                            
            else:
                self.log_with_timestamp(f"Empty file {filepath} has been created.")
                if (filepath in self.criticalFiles):
                    print(f"Malicious attempt on {filepath} made, performing forensics acquisition now!")
                    containerForensics = ContainerForensics()
                    containerForensics.save_container_image(self.containerName, "./results/output.tar")
                    containerImager = ContainerImager()
                    containerImager.create_disk_image("./results/output.tar", "./results/disk_image.img")
                    self.observer.stop()
                    exit(0)
                    # self.observer.join()
            

    def on_deleted(self, event):
        if not event.is_directory:
            filepath = "/" + self.get_file_path(event.src_path)
            self.log_with_timestamp(f"File {filepath} has been deleted.")
            if (filepath in self.criticalFiles):
                    print(f"Malicious attempt on {filepath} made, performing forensics acquisition now!")
                    containerForensics = ContainerForensics()
                    containerForensics.save_container_image(self.containerName, "./results/output.tar")
                    containerImager = ContainerImager()
                    containerImager.create_disk_image("./results/output.tar", "./results/disk_image.img")
                    self.observer.stop()
                    exit(0)
                    # self.observer.join()
        

# if __name__ == "__main__":
#     client = docker.from_env()
#     container = client.containers.get("7d47cbc3fd39")
#     monitor = FileChangesMonitor(container)
#     monitor.monitor_filechanges()
