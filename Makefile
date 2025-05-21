postgres:
	docker run --name postgres_restaurant -p 8001:5432 \
	-e POSTGRES_USER=postgres \
	-e POSTGRES_PASSWORD=postgres \
	-v postgres_data:/var/lib/postgresql/data \
	--rm \
	-d docker.arvancloud.ir/postgres:16.8

createdb:
	docker exec -it postgres_restaurant createdb --username=postgres --owner=postgres restaurant_db

dropdb:
	docker exec -it postgres_restaurant dropdb --username=postgres restaurant_db

all:
	make postgres   