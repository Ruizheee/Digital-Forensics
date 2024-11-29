import docker
import json
import time
import os

class StatisticsMonitor:
    def __init__(self, selected_container):
        self.selected_container = selected_container

    def fetch_container_stats(self):
        if self.selected_container is None:
            print("No container selected for monitoring")
            return
        else:
            try:
                for stats in self.selected_container.stats(stream=True):
                    if isinstance(stats, bytes):
                        stats = json.loads(stats.decode("utf-8"))
                    yield stats
            except Exception as e:
                print(f"Error retrieving stats {e}")

    def monitor_statistics(self):
        try:
            prev_total_cpu_usage = 0
            prev_system_cpu_usage = 0
            prev_kernel_mode_usage = 0
            prev_user_mode_usage = 0

            for stats in self.fetch_container_stats():    
                # Memory Statistics
                memory_stats = stats.get("memory_stats", {})
                stats_dict = memory_stats.get("stats", {})
                total_memory_usage = memory_stats.get("usage", 1) / (1024 * 1024)
                memory_limit = memory_stats.get("limit", 1) / (1024 * 1024 * 1024)
                inactive_memory = stats_dict.get("inactive_file", 1) / (1024 * 1024)
                active_anonymous = stats_dict.get("active_anon", 1) / (1024 * 1024)
                active_memory = total_memory_usage - inactive_memory
                memory_percent = ((active_memory / 1024) / memory_limit * 100) 

                # CPU Statistics
                total_cpu_usage = stats["cpu_stats"]["cpu_usage"]["total_usage"]
                system_cpu_usage = stats["cpu_stats"]["system_cpu_usage"]
                cpu_in_kernel_mode = stats["cpu_stats"]["cpu_usage"]["usage_in_kernelmode"]
                cpu_in_user_mode = stats["cpu_stats"]["cpu_usage"]["usage_in_usermode"]

                cpu_delta = total_cpu_usage - prev_total_cpu_usage
                system_cpu_delta = system_cpu_usage - prev_system_cpu_usage
                kernel_mode_delta = cpu_in_kernel_mode - prev_kernel_mode_usage
                user_mode_delta = cpu_in_user_mode - prev_user_mode_usage

                # Make sure we're calculating over a reasonable interval
                if system_cpu_delta > 0:
                    # Calculate the CPU usage percentage by summing all the modes
                    total_cpu_usage_sum = cpu_delta + kernel_mode_delta + user_mode_delta
                    cpu_percentage = (total_cpu_usage_sum / system_cpu_delta) * 100
                else:
                    cpu_percentage = 0

                # Update previous values for the next iteration
                prev_total_cpu_usage = total_cpu_usage
                prev_system_cpu_usage = system_cpu_usage
                prev_kernel_mode_usage = cpu_in_kernel_mode
                prev_user_mode_usage = cpu_in_user_mode


                os.system('clear')
                print(f"{'Container ID':<25} {self.selected_container.id}")
                print('=' * 30 + 'Memory Statistics' + '=' * 33)
                print(f"{'Name':<25} {self.selected_container.name}")
                print(f"{'Metric':<25} {'Value':<15}")
                print(f"{'Total Memory Usage:':<25} {total_memory_usage:.2f} {'MiB'}")
                print(f"{'Active Anonymous Memory:':<25} {active_anonymous:.2f} {'MiB'}")
                print(f"{'Active Memory:':<25} {active_memory:.2f} {'MiB'} / {memory_limit:.3f} {'GiB'}")
                print(f"{'Inactive Memory:':<25} {inactive_memory:.2f} {'MiB'}")
                print(f"{'Memory Percent:':<25} {memory_percent:.2f} {'%'}")
                print('=' * 30 + 'CPU Statistics' + '=' * 36)
                print(f"Total CPU Usage: {total_cpu_usage_sum}")
                print(f"CPU Percentage: {cpu_percentage:.2f}%")
                print('=' * 80)

                time.sleep(1)
        except ValueError as e:
            print(f"An error has occurred while monitoring the container statistics{e}")
        except KeyboardInterrupt:
            print(f"\nMonitoring stopped.")
        
# if __name__ == "__main__":
#     client = docker.from_env()
#     container = client.containers.get("7d47cbc3fd39")
#     monitor = StatisticsMonitor(client, container)
#     monitor.monitor_statistics()
