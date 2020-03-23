# Python SDK for Jason GNSS Positioning-as-a-Service

[Jason GNSS Positioning-as-a-Service](https://jason.rokubun.cat) is a cloud-based
positioning engine that uses GNSS data. One of the main features of this service
is that offers an API so that users can automatize the GNSS data processing
without the need to access the front-end.

The online documentation of the service can be found [here](https://jason.docs.rokubun.cat).


To install the package:

```bash
pip3 install jason-gnss
```

## Authentication

It is important that you have the `JASON_API_KEY` and `JASON_SECRET_TOKEN` 
environement variables. These can be fetched by accessing your area in the 
Jason PaaS and then going to `My Account` -> `API Credentials`.

## Use the package as an SDK

The package is basically a library that can be embedded into your Python scripts

```python
import jason_gnss as jason

# Submit a process without waiting for it to finish (fetch it later)
jason.submit_process(rover_file)
# ({'message': 'success', 'id': 3505}, 200)

# Get the status of your process. The documentation of the return can 
# be found in the Jason online documentation
process_id = 3505
jason.get_status(process_id)
# ({'process': {'id': 3505, ...}, 200)

# Download the results file for a given process that you own
jason.download_results(process_id)
# '/jason_gnss/rokubun_gnss_id_003505.zip'
```

## Command line tools

The package has also a command line tool so that you can use it out-of-the-box.
The following examples illustrate how to use it

```bash
export JASON_API_KEY='<jason-api-key>'
export JASON_SECRET_TOKEN='<your-private-jason-user-token>'

# Get the help
jason -h

# Process a rover file
jason process test/jason_gnss_test_file_rover.txt

# Process a rover file and adding a base station file as well
jason process test/jason_gnss_test_file_rover.txt test/jason_gnss_test_file_base.txt 

# Get the status of a process
jason status process_id

# Fetch the results file for a given process id
jason download process_id
```

## Docker execution/development

It is recommended that you use docker to execute or work with this package.
This repository contains both a `Dockerfile` as well as a `docker-compose.yml`
to help you with this.

Follow these instructions:

```bash
# Command to build the image
docker-compose build

# Start the container with the package loaded with the command
docker-compose run jason_gnss
```

Once inside the container:

```bash
# Install the package
python setup.py install
```

Now, while in the container, you can issue commands in the prompt or
within the Python console.

### API Key and secret token

If you are using docker-compose, we recommend that you store your authorization
keys in a file `.env` and run the Docker container via the command
`docker-compose run jason-gnss`. With this, your credentials will be loaded
in the container and the Jason tools will be ready to use without the need
to declare these variables.

```text
JASON_API_KEY='<jason-api-key>'
JASON_SECRET_TOKEN='<your-private-jason-user-token>'
```
