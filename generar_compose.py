import sys
import yaml


def generate_docker_compose(output_file, num_clients):
    compose_data = {
        'name': 'tp0',
        'services': {
            'server': {
                'container_name': 'server',
                'image': 'server:latest',
                'entrypoint': 'python3 /main.py',
                'environment': [
                    'PYTHONUNBUFFERED=1',
                    'LOGGING_LEVEL=DEBUG'
                ],
                'networks': ['testing_net']
            }
        },
        'networks': {
            'testing_net': {
                'ipam': {
                    'driver': 'default',
                    'config': [{
                        'subnet': '172.25.125.0/24'
                    }]
                }
            }
        }
    }

    for i in range(1, int(num_clients) + 1):
        client_name = f'client{i}'
        compose_data['services'][client_name] = {
            'container_name': client_name,
            'image': 'client:latest',
            'entrypoint': '/client',
            'environment': [
                f'CLI_ID={i}',
                'CLI_LOG_LEVEL=DEBUG'
            ],
            'depends_on': ['server'],
            'networks': ['testing_net']
        }

    with open(output_file, 'w') as f:
        yaml.dump(compose_data, f, sort_keys=False)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Uso: python3 generar_compose.py <nombre_archivo_salida> <cantidad_clientes>")
        sys.exit(1)

    output_file = sys.argv[1]
    num_clients = sys.argv[2]
    generate_docker_compose(output_file, num_clients)
