pg-start:
	docker-compose -f dc.postgres-pg.yaml up -d

pg-stop:
	docker-compose -f dc.postgres-pg.yaml stop

pg-destroy:
	docker-compose -f dc.postgre-pg.yaml down

