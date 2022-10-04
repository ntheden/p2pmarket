#!/usr/bin/env python3
from jinja2 import Template
import sys

from config import env, run_path, root_path


def docker_setup() -> None:
    with env.prefixed('P2PMARKET_'):
        api_endpoint = env('API_ENDPOINT')
    assert api_endpoint, 'P2PMARKET_API_ENDPOINT needs to be set in main.env'
    with open(root_path/'docker-compose.jinja') as f:
        template = Template(f.read())
    with open(root_path/'docker-compose.yaml', 'w') as f:
        f.write(template.render(
            run_dir=run_path,
            api_endpoint=api_endpoint
        ))


def main() -> int:
    docker_setup()
    return 0


if __name__=="__main__":
    sys.exit(main())
