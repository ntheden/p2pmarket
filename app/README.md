# Demo

Example of this app is running [here](https://p2pmarket.net)

# How to load this onto a VPS (virtual private server)

### `REACT_APP_API_ENDPOINT=http://localhost:8001 npm run build`
**The api endpoint environment variable must match your backend location, localhost is just for testing**
Builds the react app with the output in the `build` folder

### `npm install -g serve`
    `serve -s build`
Test the build. Make sure you have the backend server running and serving at `localhost:8001` (if you are following the above example build command).


### `REACT_APP_API_ENDPOINT=https://api.myp2pmkt.com npm run build`
Build the app again but place the real endpoint location, such as https://api.myp2pmkt.com

### `docker build --tag=v4sats/app-p2pmarket:latest .`
make a docker container

### `docker run -p 3000:80 -t v4sats/app-p2pmarket:latest`
test the container

# `docker images`
view containers

# `docker save v4sats/app-p2pmarket > app-p2pmarket.tar`
  `zip app-p2pmarket.tar`
  `scp app-p2pmarket.tar.gz v4sats@my-vps:./`
**v4sats is the username, and my-vps is the vps hostname or IP, change to match yours**
save archive of the container and send it to your VPS

On VPS:
gunzip app-p2pmarket.tar.gz
cat app-p2pmarket | docker load
