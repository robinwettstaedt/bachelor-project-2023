# ------------- Docker network  ------------- #

# create the custom docker network so that the containers may communicate with one another
# the containers are added to the network with the --net flag
docker network create --subnet=192.168.0.0/16 containernetwork



# ------------- Message Queue ------------- #

docker run --network=containernetwork --ip 192.168.0.22 -d --hostname rabbit-mq --name mq -p 5672:5672 -p 15672:15672 mq:latest

# wait for the rabbit mq server to start
Start-Sleep -Seconds 10



# ------------- Databases ------------- #

# Start the EPLF db
docker run --network=containernetwork --ip 192.168.0.23 --name eplf-db -d -p 3000:3000 eplf-db:latest

# Start the ZD db
docker run --network=containernetwork --ip 192.168.0.24 --name zd-db -d -p 3005:3000 zd-db:latest

# wait for the database to start
Start-Sleep -Seconds 10

# Start the container that fills the EPLF db
docker run --network=containernetwork --name fill -d -p 4000:3000 fill:latest

# wait for the database to be filled
Start-Sleep -Seconds 30



# ------------- Interface  ------------- #

docker run --network=containernetwork --name interface -d -p 5000:5000 interface:latest

# automatically open the web interface in the default browser
Start-Process "http://localhost:5000"

# wait for the interface to load
Start-Sleep -Seconds 10



# ------------- EPLF ------------- #

docker run --network=containernetwork --name eplf-publish -d -p 3001:3000 eplf-publish:latest
docker run --network=containernetwork --name eplf-republish -d -p 3003:3000 eplf-republish:latest
docker run --network=containernetwork --name eplf-validation -d -p 3004:3000 eplf-validation:latest



# ------------- ZD ------------- #


docker run --network=containernetwork --name zd-listen -d -p 3006:3000 zd-listen:latest
docker run --network=containernetwork --name zd-listen2 -d -p 3007:3000 zd-listen:latest
docker run --network=containernetwork --name zd-listen3 -d -p 3008:3000 zd-listen:latest

docker run --network=containernetwork --name zd-validation -d -p 3009:3000 zd-validation:latest



# ------------- Validator ------------- #

docker run --network=containernetwork --name validator-listen -d -p 30010:3000 validator-listen:latest
docker run --network=containernetwork --name validator-publish -d -p 3011:3000 validator-publish:latest


