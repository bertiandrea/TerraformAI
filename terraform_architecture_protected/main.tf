terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0.0"
    }
  }
}

provider "docker" {}

# Crea una rete Docker personalizzata
resource "docker_network" "custom_network" {
  name = "custom_network"
}

# Configura l'immagine del database PostgreSQL
resource "docker_image" "postgres" {
  name         = "postgres:latest"
  keep_locally = false
}

# Configura un container PostgreSQL
resource "docker_container" "postgres" {
  name  = "db_container"
  image = docker_image.postgres.name
  networks_advanced {
    name = docker_network.custom_network.name
  }

  env = [
    "POSTGRES_USER=admin",
    "POSTGRES_PASSWORD=password",
    "POSTGRES_DB=myappdb"
  ]

  ports {
    internal = 5432
    external = 5432
  }

  restart = "always"
}

# Configura l'immagine del backend Python/Flask
resource "docker_image" "backend" {
  name         = "python:3.9-slim"
  keep_locally = false
}

# Configura il container per il backend
resource "docker_container" "backend" {
  name  = "backend_container"
  image = docker_image.backend.name
  networks_advanced {
    name = docker_network.custom_network.name
  }

  env = [
    "DATABASE_HOST=db_container",
    "DATABASE_USER=admin",
    "DATABASE_PASSWORD=password",
    "DATABASE_NAME=myappdb"
  ]

  ports {
    internal = 5000
    external = 5000
  }

  command = ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]
  restart = "always"
}

# Configura l'immagine del frontend Nginx
resource "docker_image" "nginx" {
  name         = "nginx:latest"
  keep_locally = false
}

# Configura il container per il frontend
resource "docker_container" "nginx" {
  name  = "frontend_container"
  image = docker_image.nginx.name
  networks_advanced {
    name = docker_network.custom_network.name
  }

  ports {
    internal = 80
    external = 8080
  }

  volumes {
    host_path      = "/nginx.conf" # Cambia con il percorso assoluto
    container_path = "/nginx.conf"
  }

  restart = "always"
}

############################################################################################################
# Aggiunge un contenitore fittizio per la deception
resource "docker_image" "deception" {
  name         = "busybox"
  keep_locally = false
}

resource "docker_container" "deception" {
  name  = "deception_container"
  image = docker_image.deception.name
  networks_advanced {
    name = docker_network.custom_network.name
  }

  command = ["sh", "-c", "while true; do echo 'Deception Active'; sleep 60; done"]
  ports {
    internal = 1234
    external = 1234
  }

  restart = "always"
}

# Aggiunge un contenitore per l'aspetto di un server di monitoraggio
resource "docker_image" "monitoring" {
  name         = "prom/prometheus"
  keep_locally = false
}

resource "docker_container" "monitoring" {
  name  = "monitoring_container"
  image = docker_image.monitoring.name
  networks_advanced {
    name = docker_network.custom_network.name
  }

  ports {
    internal = 9090
    external = 9090
  }

  restart = "always"
}
############################################################################################################

