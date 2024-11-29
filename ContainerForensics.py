import docker
import os

# DOCKER_CLIENT = docker.from_env()
# CONTAINERS = DOCKER_CLIENT.containers.list(all=True)

class ContainerForensics:
    def __init__(self):
        self.client = docker.from_env()
        self.containers = self.client.containers.list(all=True)

    def save_container_image(self, container_name, output_path):

        try:
            # Get the container object
            container = self.client.containers.get(container_name)

            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)  # Create the directory if it doesn't exist

            # Export the container filesystem
            with open(output_path, 'wb') as f:
                for chunk in container.export():
                    f.write(chunk)
            print(f"Container filesystem saved to {output_path}")

        except docker.errors.NotFound:
            print(f"Container '{container_name}' not found.")
        except Exception as e:
            print(f"An error occurred: {e}")

'''
# Usage
container_name = "lol"  # Replace with the actual container name or ID
output_path = "output.tar"      # Replace with desired output path
save_container_image(container_name, output_path)
'''
