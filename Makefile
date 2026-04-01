DOCKER_COMPOSE = docker compose

.PHONY: setup up down restart build clean help

help:
	@echo "Comandos disponíveis:"
	@echo "  make install  - Configura permissões e sobe o ambiente do zero"
	@echo "  make up       - Sobe os containers (se já construídos)"
	@echo "  make build    - Constrói as imagens e sobe os containers"
	@echo "  make down     - Para e remove os containers e redes"
	@echo "  make restart  - Reinicia os containers"
	@echo "  make clean    - Remove volumes (CUIDADO: apaga os dados do banco e Solr)"

setup:
	@echo "🔧 Resetando e configurando permissões..."
	@mkdir -p logs dags plugins data
	sudo chown -R $(shell id -u):0 logs dags plugins data
	sudo chmod -R 775 logs dags plugins data
	@if [ ! -f .env ]; then \
		echo "📝 Criando arquivo .env..."; \
		cp .env.example .env; \
	fi

build:
	@echo "🚀 Construindo e subindo o ambiente Docker..."
	$(DOCKER_COMPOSE) up -d --build

up:
	@echo "🚀 Subindo o ambiente Docker..."
	$(DOCKER_COMPOSE) up -d

down:
	@echo "🫠 Parando o ambiente Docker..."
	$(DOCKER_COMPOSE) down

restart:
	@echo "🔄 Reiniciando o ambiente Docker..."
	$(DOCKER_COMPOSE) restart

install: setup build