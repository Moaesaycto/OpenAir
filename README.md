# OpenAir

Type: Application / Live Tracker · Tech Stack: Python, Typescript, Uvicorn · Hardware: RTL-SDR, GPS · Status: Active

## Installation
In the root directory, simply run `./OpenAir build`. The output in the `dist` directory will be the file.

## Development Setup

All the scripts that you need to run for development can be handled through the `./OpenAir` script.

To setup the environment, you can simply run:

```bash
./OpenAir setup <your OS>
```

Right now, only MacOS is set up. Linux will be supported in the future.

For development servers, you can run each major component individually or together.

```bash
# To run the server
./OpenAir run server

# To run the client
./OpenAir run client

# To run both at the same time
./OpenAir run
```

These development servers support live updates.

