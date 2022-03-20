# Chapter-02: Modern Python Development Environments

## Virtualization with Docker

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

  Consider below compose file content

  ```yaml
  version: '3.8'
  services:
    echo-service:
      build: .
      ports:
      - "5000:5000"
      tty: true
    database-service:
      image: postgres
      restart: always
  ```

  This file defines two services, `echo-service` and `database-service`, when `echo-service` want to communicate with `database-service`, it can use `database-service:5432` directly without knowing its hostname or IP address. Similarly, other services can address `echo-service` using `echo-service:5000` directly. Whereas the best practice is still using `environment` section to define environment variables for these service names, such as:

  ```yaml
  version: '3.8'
  services:
    echo-service:
      build: .
      ports:
      - "5000:5000"
      tty: true
      # Environment section, so that your application doesn't need to hardcode these service names in your code
      environment:
        - DATABASE_HOSTNAME=database-service
        - DATABASE_PORT=5432
        - DATABASE_PASSWORD=password
    database-service:
      image: postgres
      restart: always
      environment:
        POSTGRES_PASSWORD: password
  ```

  Environment variables are the most recommended way of providing configuration parameters for containers.

- **Communicating between docker compose environments**

  By default, if you have multiple docker compose applications the network that created by compose for a single application is isolated from the networks of other applications. In order for multiple independent applications to communicate with each other, you can define a <u>named external docker network</u> as the default network for all services

  ```yaml
  version: '3.8'
  # Use external network
  networks:
    default:
      external:
        name: my-interservice-network
  services:
    webserver:
      build: .
      ports:
      - "80:80"
      tty: true
      environment:
        - DATABASE_HOSTNAME=database
        - DATABASE_PORT=5432
        - DATABASE_PASSWORD=password
    database:
      image: postgres
      restart: always
      environment:
        POSTGRES_PASSWORD: password
  ```

  Such external networks are not managed by docker compose, so you will need to create the network manually as: `docker network create my-interservice-network`. Once the network is created, you can use it in other docker-compose files for all applications that should have their registered in the same network. For example:

  ```yaml
  version: '3.8'
  # Use external network
  networks:
    default:
      external:
        name: my-interservice-network
  services:
    other-service:
      build: .
      ports:
      - "80:80"
      tty: true
      environment:
        - DATABASE_HOSTNAME=database
        - DATABASE_PORT=5432
        - ECHO_SERVER_ADDRESS=http://echo-server:80
  ```

- **Delaying application startup until service ports are open**

  You can also control to some extent the order of service startup when you run `docker-compose up`, for example:

  ```yaml
  version: '3.8'
  services:
    echo-server:
      build: .
      ports:
      - "5000:5000"
      tty: true
      # Controls echo-server depends on database to start first
      depends_on:
        - database
    database:
      image: postgres
      environment:
        POSTGRES_PASSWORD: password
  ```

  But there is something to be noted here, docker-compose only make sure that the service will be **started** in order, but will not make sure the PostgreSQL will be ready to actually accept connections, because PostgreSQL might take couple of seconds for initialization. What you really need here is to test if the port of 5432 is available, for example, using [wait-for-it](https://wait-for-it.readthedocs.io/en/latest/) tool as:  `wait-for-it --service <service-address> -- command [...]`, where `[...]` represents any set of arguments for `command`

  ```yaml
  version: '3.8'
  services:
    echo-service:
      build: .
      ports:
        - "5000:5000"
      tty: true
      volumes:
        - type: bind
          source: ./app
          target: /app/
      environment:
        - FLASK_ENV=development
      command:
        # This wait-for-it will ensure the echo-server starts only when it would be able to connect to the database
        wait-for-it --service database-service:5432 --timeout=0 --
        python /app/echo.py
    database-service:
      image: postgres
      environment:
        POSTGRES_PASSWORD: password
  ```

- **Adding live reload for absolutely any code**

  We've covered this part earlier, which suggests that the best way to provide code to the container while working with docker in the development stage is through docker volumes.

  But this only works when the framework you use supports active hot reloading. In the scenarios when this is not the case, [watchdog[watchmedo ]](https://pypi.org/project/watchdog/) might be helpful. The basic usage is: `watchmedo auto-restart --patterns "*.py" --recursive -- command [...]`

  The `--patterns "*.py"` options indicate which files the `watchmedo` process should monitor for changes. The `--recursive` flag makes it traverse the current working directory recursively so it will be able to pick up changes made even if they are nested deep down in the directory tree. The `-- command [...]` usage pattern is the same as the `wait-for-it` command 

  If you installed `watchdog` in the docker image, then the compose file can be modified as:

  ```yaml
  version: '3.8'
  services:
    echo-server:
      build: .
      ports:
      - "5000:5000"
      tty: true
      depends_on:
        - database
      command:
        watchmedo auto-restart --patterns "*.py" --recursive --
        python echo.py
      volumes:
        - .:/app/
  ```

  The above Docker Compose setup will restart the process inside of a container every time there is a change to your Python code.

## Virtualization with Vagrant

### 
