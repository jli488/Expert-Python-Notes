# Chapter-02: Modern Python Development Environments

## Virtualization

### Docker, docker-compose, and poetry

This repo demonstrates an operating system virtualization method using *Dockerfile* and *docker-compose.yml* . At the mean time, it might be useful of using [*poetry*](https://python-poetry.org/) for dependency management.

Some modifications compare to the script introduced in the *Dockerfile* and *docker-compose.yml* introduced in the book:

- Dockerfile, this can be used to essentially virtualize the **environment** of an application, without any application code copied into the container

  ```dockerfile
  FROM python:3.9-slim
  
  # This argument can be used if you want to differentiate prod and dev environment build
  ARG BUILD_ENV=development
  
  WORKDIR /dev_env/
  
  # This can be simplified to: RUN pip install "poetry==$POETRY_VERSION" if poetry is used for dependency management
  COPY requirements.txt poetry.lock pyproject.toml /dev_env/
  
  # Config poetry to NOT create a virtual environment before install any packages, since we are already in a virtualized environment
  RUN pip install -r requirements.txt && \
      poetry config virtualenvs.create false && \
      poetry install $(test "$BUILD_ENV" == "production" && echo "--no-dev") --no-interaction --no-ansi
  ```

- docker-compose.yml, this can be used to mount the application directory and run the application in the environment virtualized in the Dockerfile. Mount volume can help you to do interactive development without rebuild and rerun the image

  ```yaml
  version: '3.8'
  services:
    echo-service:
      # Build the echo service using Dockerfile in previous section
      build: .
      ports:
        - "5000:5000"
      tty: true
      volumes:
        # Mount the volume of the application
        - type: bind
          source: ./app
          target: /app/
      environment:
        - FLASK_ENV=development
      command:
        # Run the application
        python /app/echo.py
  ```

### Useful Docker and Docker Compose recipes for Python

- **Reducing the size of containers**

  It is recommended to have a separate image for every service with a container-based approach. This means that with a lot of services, the storage overhead may become noticeable. Two techniques to reduce the image size:

  - Use a base image that is designed for this purpose, e.g. Alpine Linux, which is an example of compact Linux distribution
  - Take into consideration the characteristics of the Docker overlay filesystem. Docker images consists of layers, where each layer encapsulates the difference in the root filesystem between itself and the previous layer. This means that doing multiple `RUN` instructions can help avoid excessive layer commits

  Taking into the above considerations, we could come up with a new Dockerfile:

  ```dockerfile
  FROM python:3.9-alpine
  
  ARG BUILD_ENV=development
  
  WORKDIR /dev_env/
  
  COPY requirements.txt poetry.lock pyproject.toml /dev_env/
  RUN apk add --no-cache gcc libffi-dev musl-dev && \
      pip3 install -r requirements.txt && \
      poetry config virtualenvs.create false && \
      poetry install $(test "$BUILD_ENV" == "production" && echo "--no-dev") --no-interaction --no-ansi && \
      apk del gcc libffi-dev musl-dev
  ```

  The above image based from `python:3.9-alpine`, which is a more compact form of python base image, and provide python version control at the mean time. Notice that we also need to manually install some required libraries for building the environment now, such as gcc, libffi-dev, etc.

  With the modification, the image size reduced from ~180MB to ~110MB

- **Addressing services inside of a docker compose environment**

  
