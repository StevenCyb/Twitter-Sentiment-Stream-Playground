docker-compose down
docker stop $(docker ps -a -q)
docker rm $(docker ps -a -q)
docker network rm `docker network ls -q`