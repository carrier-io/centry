from os import environ
# environ["CORE_CONFIG_SEED"] = "file:config/pylon.yml"
# environ["CORE_DEVELOPMENT_MODE"] = 'true'
from dotenv import load_dotenv

localhost = '127.0.0.1'
# environ["APP_HOST"] = f"http://{localhost}"


load_dotenv('./.env')

# environ["APP_HOST"] = 'http://127.0.0.1:8080'

print(f'{environ["APP_HOST"]=}')

def setenv(key, value):
    environ[key] = value


# import docker
# client = docker.DockerClient()
def get_container_ip(name: str, network_name: str = 'centry_pylon'):
    # container = client.containers.get(name)
    # ip = container.attrs['NetworkSettings']['Networks'][network_name]['IPAddress']
    ip = localhost
    print(name, ip)
    return ip


setenv('REDIS_HOST', get_container_ip('carrier-redis'))
setenv('RABBIT_HOST', get_container_ip('carrier-rabbit'))
setenv('POSTGRES_HOST', get_container_ip('carrier-postgres'))
setenv('VAULT_URL', f'http://{get_container_ip("carrier-vault")}:8200')
setenv('MINIO_HOST', f'http://{get_container_ip("carrier-minio")}:9000')


from pylon import main

main.main()
