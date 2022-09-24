# Docker

## Prerequisites

* Git
* <a href="https://docs.docker.com/engine/install/" target="_blank">Docker</a>
* <a href="https://docs.docker.com/compose/install/" target="_blank">Docker Compose</a>

## Setup

### Using Prebuilt docker images
  * Download [docker-compose.yml](https://github.com/iamrony777/javinfo-api/blob/main/docker-compose.yml) and [.env](https://github.com/iamrony777/javinfo-api/blob/main/.env.sample) 

    ```bash
    wget https://raw.githubusercontent.com/iamrony777/javinfo-api/main/docker-compose.yml
    wget https://raw.githubusercontent.com/iamrony777/javinfo-api/main/.env.sample -O ".env"
    ```

  * Check [Variables](../#variables-options-descriptions) and modify in **.env**
    ```bash
    # Required variables for docker-compose
    API_PASS=admin
    API_USER=admin
    PLATFORM=container
    CREATE_REDIS=false # `false` because using redis in another container

    ...
    ```
  * Review `docker-compose.yml`
    ```bash
    docker compose convert
    ```
  * Start compose
    ```bash
    docker compose -f "docker-compose.yml" --env-file ".env" up --detach
    ```

### Building Docker images
  * Clone this [Repo](https://github.com/iamrony777/javinfo-api) locally
    ```bash
    git clone https://github.com/iamrony777/javinfo-api
    ```
  * Uncomment `build` in **services:api**

  <div align="center"><img src="../..//assets/images/docker_compose_service:api:build_comment.webp"></img> <img src="../../assets/images/docker_compose_service:api:build_uncomment.webp"></img></div>

  * Edit .env file
    ```bash
    cp .env.sample .env
    vim .env # nano .env 
    ```
  * Check [Variables](../#variables-options-descriptions) and modify in .env
    ```bash
    # Required variables for docker-compose
    API_PASS=admin
    API_USER=admin
    PLATFORM=container
    CREATE_REDIS=false # `false` because using redis in another container

    ...
    ```
  * Review `docker-compose.yml`
    ```bash
    docker compose convert
    ```
  * Start compose
  ```bash
  docker compose -f "docker-compose.yml" --env-file ".env" up --detach --build
  ```
  
