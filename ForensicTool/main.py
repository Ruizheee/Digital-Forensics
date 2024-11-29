import docker
from Selector import Selector

DOCKER_CLIENT = docker.from_env()
CONTAINERS = DOCKER_CLIENT.containers.list(all=True)

def main():
    app = Selector(CONTAINERS, DOCKER_CLIENT)
    app.run()

if __name__ == '__main__':
    main()