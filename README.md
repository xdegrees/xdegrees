# X Degrees

Find connections between people in the Whitepages identity graph!

The application is built with the [Tornado framework][http://www.tornadoweb.org/en/stable/] and
includes the following web services:
* /version: retrieve information about the build version
* /separations: find links between two people

The project also has a web UI for search interactions. The UI is built with Bootstrap and jQuery.

## Development

### Setting up Python
The easiest way to set up your Python environment is within a virtualenv.

These instructions assume you're using virtualenv rather than Anaconda. Here's how to get it:
[virtualenv][http://python-guide-pt-br.readthedocs.io/en/latest/dev/virtualenvs/]

Run the following within the project root; note that you must specify a python3 interpreter:
```sh
virtualenv -p /usr/local/bin/python3 venv
source venv/bin/activate
pip install --upgrade -e .
```

### Running tests
To run tests:
```sh
source venv/bin/activate
pip install --upgrade --requirement requirements-tests.txt
python setup.py test
```

To run static analysis:
```sh
source venv/bin/activate
pip install --upgrade --requirement requirements-analysis.txt
prospector -s high
```

## Running the code

### Running without Docker
You can run the server without Docker as follows.

First, start the other microservice:
```sh
docker run -it -p 3000:3000 --env-file ./.env.production challenge-api:latest
```

Then, start the server:
```sh
source venv/bin/activate
python -m xdegrees.app --search-url='http://localhost:3000/v1/separations' --port=1792
```

To confirm that the server is working, check the /version endpoint:
```sh
curl http://localhost:1792/version
```

To see all command line parameters, including default values:
```sh
source venv/bin/activate
python -m xdegrees.app --help
```

### Running with Docker
Or, you can use the provided Dockerfile to build and deploy a docker image. Note that to get your
containers to communicate, they need to be on the same network. The following instructions show how
to do this by hand, but you also could do it with other tools like Docker Compose.

First, start the other microservice. Note that we specify the network here:
```sh
docker run -it -p 3000:3000 --env-file ./.env.production --network my_network --name challenge-api challenge-api:latest
```

Then, update the SEARCH_URL in your local .env.development file to connect to the microservice by name:
SEARCH_URL=http://challenge-api:3000/v1/separations

Finally, use Docker to start the server on the same network as above:
```sh
docker build -t xdegrees .
docker run -it -p 1792:1792 --env-file ./.env.development --network my_network --name xdegrees  xdegrees:latest
```

To confirm that the server working, check the /version endpoint:
```sh
curl http://localhost:1792/version
```

### Monitoring
Basic monitoring is available via the /version endpoint.

### Logging
Logging is to stdout and stderr.

## Future work
The following work would have to be done in order to move the application to a production setting:
* Use async handlers within tornado, since the call out to the WhitePages API is slow and we want the service to
keep working while it's blocking on API calls.
* Put the application behind a load balancer, and terminate TLS in front of the application.
* Integrate the application into a metrics and monitoring system.
* Separate unit tests vs integration tests vs performance tests.
* Actually document the APIs using a standard tool. Decide on an API version strategy.
* Do or remove miscellaneous "TODO" comments in the source code.

## Compatibility
This project is compatible with:
* Python 3.5
* Docker 17

## License
This library is released under the MIT license; see LICENSE for details.
