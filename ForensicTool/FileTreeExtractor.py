import docker
import time
import os
import subprocess
from datetime import datetime

class FileTreeExtractor:
    '''
    Command: docker inspect <container_id> | grep MergedDir
    '''
    def __init__(self, container):
        self.container = container
        self.containerID = self.container.id
        self.containerName = self.container.name

    def locate_merged_layer(self):
        try:
            merged_layer_result = subprocess.run(
                f"docker inspect {self.containerID} | grep MergedDir",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            if merged_layer_result.returncode == 0:
                merged_layer = merged_layer_result.stdout.strip().split(':')[-1].strip().strip('",')
                return merged_layer
            else:
                raise Exception(f"Error locating the Merged Layer of the container {merged_layer_result.stderr}")

        except Exception as e:
            print(f"An error has occurred {e}")
            return None

    def extract_filetree(self):
        merged_layer = self.locate_merged_layer()

        if merged_layer:
            output_file = "filetree.txt"
            command = ["tree", merged_layer]

            with open(output_file, "w") as file:
                try:
                    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    filetree_output = f"Timestamp: {timestamp}\n" + "\n".join(result.stdout.splitlines()[1:]) + "\n"
                    file.write(filetree_output)
                    print(f"A copy of the File Tree in the {self.containerName} can be found in {output_file}.")
                except subprocess.CalledProcessError as e:
                    print(f"An error has occurred while saving to {output_file}.")

# if __name__ == "__main__":
#     client = docker.from_env()
#     container = client.containers.get("7d47cbc3fd39")
#     extractor = FileTreeExtractor(container)
#     extractor.extract_filetree()
