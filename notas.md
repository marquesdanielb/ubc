## Arquitetura do sistema
- dags 
- logs
- plugins
- docker
- data
- scripts
- tests

## Rodar o comando permitindo o usuário do airflow de acessar diretórios de dags e etc...
sudo chown -R 5000:0 logs dags plugins data