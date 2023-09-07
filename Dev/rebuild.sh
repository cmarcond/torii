docker compose -f docker_compose_torii.yml down -v
docker rmi -f dev-torii 
docker compose -f docker_compose_torii.yml up --build -d
docker compose -f docker_compose_torii.yml logs -f torii

