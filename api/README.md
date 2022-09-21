### P2P Market API

# to test outside of docker:
PYTHONPATH=./app uvicorn --port=8001 --reload app.main:app

`deploy/sample-docker-compose.yaml` can be copied to `deploy/docker-compose.yaml` and modified. Or, run `docker_setup.py` after copying `sample_env` to `main.env` and modifying it to match your configuration.

docker build --tag=v4sats/p2pmarket-api:latest .

# to test:
docker run -p 8001:80 -it  -e PYTHONPATH=/code/app --mount type=bind,source="$(pwd)"/run,target=/code/run v4sats/p2pmarket-api:latest

# and to get a prompt to debug something, add /bin/bash to the end
docker run -p 8001:80 -it  -e PYTHONPATH=/code/app --mount type=bind,source="$(pwd)"/run,target=/code/run v4sats/p2pmarket-api:latest /bin/bash

# and run:
root@myvps:/code# uvicorn --host=0.0.0.0 --port=80  app.main:app

# to deploy:
docker-compose up -d
