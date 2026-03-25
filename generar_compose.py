import sys
import yaml


def generate_docker_compose(output_file, num_clients):
    compose_data = {
        'services': {
            'server': {
                'container_name': 'server',
                'image': 'server:latest',
                'entrypoint': 'python3 /main.py',
                'environment': [
                    'PYTHONUNBUFFERED=1',
                ],
                'networks': ['testing_net'],
                'volumes': [
                    './server/config.ini:/config.ini'
                ]
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
                'CLI_LOG_LEVEL=DEBUG',
                f'CLI_NOMBRE=Cliente {i}',
                'CLI_APELLIDO=_',
                'CLI_DOCUMENTO=12345678',
                'CLI_NACIMIENTO=1999-01-01',
                f'CLI_NUMERO={7000 + i}'
            ],
            'depends_on': ['server'],
            'networks': ['testing_net'],
            'volumes': [
                './client/config.yaml:/config.yaml',
                f'./.data/agency-{i}.csv:/.data/agency-{i}.csv'
            ]
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
