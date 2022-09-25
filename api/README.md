### P2P Market API

# Development Setup:
## Non-Docker:
python3 -m pip install -r requirements
PYTHONPATH=./app uvicorn --port=8001 --reload app.main:app


# Deployment Setup:
In main.env, set `P2PMARKET_API_ENDPOINT`, which will be the domain name. This is used by the proxy server and to generate a certificate for https


# to test outside of docker:
PYTHONPATH=./app uvicorn --port=8001 --reload app.main:app

`deploy/sample-docker-compose.yaml` can be copied to `deploy/docker-compose.yaml` and modified. Or, run `docker_setup.py` after copying `sample_env` to `main.env` and modifying it to match your configuration.

docker build --tag=v4sats/api-p2pmarket:latest .

# to test:
docker run -p 8001:80 -it  -e PYTHONPATH=/code/app --mount type=bind,source="$(pwd)"/run,target=/code/run v4sats/api-p2pmarket:latest

# and to get a prompt to debug something, add /bin/bash to the end
docker run -p 8001:80 -it  -e PYTHONPATH=/code/app --mount type=bind,source="$(pwd)"/run,target=/code/run v4sats/api-p2pmarket:latest /bin/bash

# and run:
root@myvps:/code# uvicorn --host=0.0.0.0 --port=80  app.main:app

# to deploy:
docker-compose up -d
