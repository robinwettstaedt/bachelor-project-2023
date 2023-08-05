# ------------- Stop and remove the EPLF containers  ------------- #

docker stop eplf-publish
docker rm eplf-publish

docker stop eplf-republish
docker rm eplf-republish

docker stop eplf-listen
docker rm eplf-listen


docker stop eplf-db
docker rm eplf-db

docker stop fill
docker rm fill


# ------------- Stop and remove the ZD containers  ------------- #

docker stop zd
docker rm zd

docker stop zd2
docker rm zd2

docker stop zd3
docker rm zd3


docker stop zd-db
docker rm zd-db


# ------------- Stop and remove the Message Queue containers  ------------- #

docker stop mq
docker rm mq


# ------------- Stop and remove the web interface containers  ------------- #

docker stop interface
docker rm interface



# ------------- Remove the Docker network ------------- #

docker network rm containernetwork