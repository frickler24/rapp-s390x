# vim:set ft=Makefile ts=8:

it:	clean netzwerk mariadb pmaneu hap
con:	it rappprod
coni:   it image rappprod
all:	it image codefile rapptest rappprod status

clean:
	-docker stop -t 2 mariadb
	-docker rm -f rapp
	-docker rm -f pma
	-docker rm -f mariadb
	-docker rm -f hap
	-docker network rm mariaNetz

netzwerk:
	docker network create --subnet 10.42.0.0/24 mariaNetz

hap:
	-docker run -d \
		--name hap \
		--publish 8088:80 \
		--publish 18443:443 \
		--network mariaNetz \
		--network-alias hap \
		-e TZ='Europe/Berlin' \
		-v $$PWD/other_files/haproxy:/usr/local/etc/haproxy:ro \
		-v $$PWD/other_files/certs:/certs:ro \
		haproxy:2.5.1 haproxy -f /usr/local/etc/haproxy/haproxy.cnf -d -V


mariadb:
	docker run -d \
		--name mariadb \
		--network mariaNetz \
		--network-alias maria \
		--restart unless-stopped \
		-e TZ='Europe/Berlin' \
		-e MYSQL_ROOT_PASSWORD=+++HvgMPR*** \
		-v /home/linux1/datadir:/var/lib/mysql \
		-v $$PWD/mariadbconf.d:/etc/mysql/conf.d \
		mariadb:10.7

pmaneu:
	docker run -d \
		--name pma \
		--network mariaNetz \
		--network-alias pma \
		--restart unless-stopped \
		-e TZ='Europe/Berlin' \
		-e PMA_HOST=maria \
		-e MYSQL_ROOT_PASSWORD=+++HvgMPR*** \
		phpmyadmin:5
	docker exec -it pma sh -c "cd /var/www/html && mkdir -p pma && cd pma && ( cp -R ../* . || true ) && rm -rf pma && chmod 777 /var/www/html/pma/tmp"


image:
	docker build -t rapp -f dockerfiles/Dockerfile_full .


rapptest:
	docker run -it --rm \
		--name testDjango \
		--network mariaNetz \
		-e TZ='Europe/Berlin' \
		-v $$PWD/.env.docker:/RApp/.env \
		rapp:latest sh -c "/RApp/manage.py test --no-input"

rappprod:
	docker run -d \
		--name rapp \
		--publish 8989:8000 \
		--network mariaNetz \
		--network-alias rapp \
		--restart unless-stopped \
		-e TZ='Europe/Berlin' \
		rapp:latest

status:
	sleep 1
	docker ps

vieleweg:
	@echo $(shell bash -c 'for i in {1..10}; do docker rm -f rapp$$i; done')

rappviele: vieleweg
	@echo $(shell bash -c 'for i in {1..10}; do \
		docker run -d \
			--name rapp$$i \
			--network mariaNetz \
			--network-alias rapp$$i \
			--restart unless-stopped \
			-e TZ='Europe/Berlin' \
			-v $$PWD:/RApp \
			-v $$PWD/.env.docker:/RApp/.env \
			rapp:latest; done')

vorbereitung:
	-docker rm -f hap
	make hap_port80und443
	@echo "Ports 80 und 443 freischalten im Router für den Docker-Host, dann <Return>"
	@read a

letsencrypt: vorbereitung
	docker run -it \
		--rm \
		--name certcont \
		--ip=10.42.0.99 \
		--network mariaNetz \
		--network-alias letsencrypt \
		--volume "$$PWD/other_files/letsencrypt/etc:/etc/letsencrypt:rw" \
		--volume "$$PWD/other_files/letsencrypt/var:/var/lib/letsencrypt:rw" \
		certbot/certbot:latest \
			certonly --standalone \
				-d frickler.eichler-web.de \
				--non-interactive \
				--preferred-challenges http \
				--agree-tos \
				--email m5@frickler24.de \
				--http-01-port=80
				sudo chown lutz $$PWD/other_files/letsencrypt/etc/live/frickler.eichler-web.de/privkey.pem
		cat $$PWD/other_files/letsencrypt/etc/live/frickler.eichler-web.de/fullchain.pem \
			$$PWD/other_files/letsencrypt/etc/live/frickler.eichler-web.de/privkey.pem \
			> $$PWD/other_files/certs/RApp.pem
		docker rm -f hap
		make hap
		@echo
		@echo "Nun die Ports 80 und 443 wieder auf den ursprünglichen Stand zurücksetzen".

hap_port80und443:
	-docker run -d \
		--name hap \
		--restart unless-stopped \
		--publish 80:80 \
		--publish 443:443 \
		--publish 8088:80 \
		--publish 18443:443 \
		--network mariaNetz \
		--network-alias hap \
		--restart unless-stopped \
		-e TZ='Europe/Berlin' \
		-v $$PWD/other_files/haproxy:/usr/local/etc/haproxy:ro \
		-v $$PWD/other_files/certs:/certs:ro \
		haproxy haproxy -f /usr/local/etc/haproxy/haproxy.cnf -d -V

