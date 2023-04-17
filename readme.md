## gallery-dl API Server

This repository contains a simple REST API server for [gallery-dl](https://github.com/mikf/gallery-dl), a command-line program to download image galleries and collections from various websites. The API allows users to download galleries or albums from supported sites using `gallery-dl` through an API endpoint.

## Prerequisites

- Python 3.9 or higher
- Docker (optional, for running the application in a container)

## Installation

1. Clone the repository:
```
git clone https://github.com/JoshuaAFerguson/gallery-dl-api-server.git
cd gallery-dl-api-server
```

2. Install the required Python packages:
```
pip install -r requirements.txt
```
## Usage

1. Start the REST API server by running the Python script:
```
python gallery_dl_api.py
```
The API will be accessible at `http://0.0.0.0:5000/download`.

2. To use the API, send a POST request to the `/download` endpoint with the URL of the gallery or album you want to download. Here's an example of how to do this using `curl`:
```
curl -X POST -H "Content-Type: application/json" -d '{"url": "https://example.com/gallery"}' http://0.0.0.0:5000/download
```
Make sure to replace `"https://example.com/gallery"` with the actual URL of the gallery or album you want to download.

## Building the Docker image

To run the application in a Docker container, you can use the provided Dockerfile. Build the Docker image and run the container with the following commands:

Building the Docker image:
```
docker build -t gallery-dl-api .
```
## Running in docker

### Run the Docker container:

```
docker run -p 5000:5000 -d s0v3r1gn/gallery-dl-api:latest
```
### Alternately use docker compose:

1. Edit the [docker-compose.yml](docker-compose.yml) file

2. Run docker compose
```
docker compose up -d
```
or 
```
docker-compose up -d
```
## Exposing the download 

```
docker run -p 5000:5000 -v ~/downloads:/app/gallery-dl -d gallery-dl-api
```
## Exposing the configuration file

```
docker run -p 5000:5000 -v ~/gallery-dl.conf:/app/gallery-dl.conf -d gallery-dl-api
```

The REST API will be accessible at `http://localhost:5000/download`.

## Prebuilt Docker hub image

[Docker hub](https://hub.docker.com/r/s0v3r1gn/gallery-dl-api-server)

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Feel free to submit pull requests, create issues, or suggest enhancements.

## Disclaimer

This project is for educational purposes only. Please respect the rights of content creators and follow the terms of service of the websites from which you are downloading content.
