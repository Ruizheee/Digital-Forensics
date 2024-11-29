import keyboard
from ProcessMonitor import ProcessMonitor
from NetworkMonitor import NetworkMonitor
from StatisticsMonitor import StatisticsMonitor
from FileChangesMonitor import FileChangesMonitor
from FileTreeExtractor import FileTreeExtractor

class Selector:
    def __init__(self, containers, docker_client):
        self.selected_container = None
        self.containers = containers
        self.docker_client = docker_client

    def display_container_information(self):
        print("Available Containers: ")
        for number, container in enumerate(self.containers, start=1):
            print(f"{number}. ID: {container.short_id}, Name: {container.name}, Status: {container.status}")
        
    def select_container(self):
        self.display_container_information()
        try: 
            choice = int(input("Select a container by number: "))
            container_id = self.containers[choice - 1].short_id
            self.selected_container = self.docker_client.containers.get(container_id)
        except (IndexError, ValueError):
            print("Invalid choice. Please try again.")

    def menu(self):
        while True:
            print("\nMain Menu: ")
            print("1. Monitor New Processes")
            print("2. Monitor Network Connections")
            print("3. Monitor Container Statistics")
            print("4. Monitor File Changes")
            print("5. Save File Tree to a File")
            choice = input("Choose an option: ").strip()

            if choice == '1':
                processes_tool = ProcessMonitor(self.selected_container)
                processes_tool.monitor_processes()
            elif choice == '2':
                network_tool = NetworkMonitor(self.selected_container)
                network_tool.monitor_network()
            elif choice == '3':
                stats_tool = StatisticsMonitor(self.selected_container)
                stats_tool.monitor_statistics()
            elif choice == '4':
                file_tool = FileChangesMonitor(self.selected_container)
                file_tool.monitor_filechanges()
            elif choice == '5':
                tree_tool = FileTreeExtractor(self.selected_container)
                tree_tool.extract_filetree()
            else:
                print("Invalid Choice")
    
    def run(self):
        self.select_container()
        self.menu()

