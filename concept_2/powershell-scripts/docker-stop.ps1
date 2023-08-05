# ------------- Stop and remove the EPLF containers  ------------- #

docker stop eplf-publish
docker rm eplf-publish

docker stop eplf-republish
docker rm eplf-republish

docker stop eplf-validation
docker rm eplf-validation


docker stop eplf-db
docker rm eplf-db

docker stop fill
docker rm fill


# ------------- Stop and remove the ZD containers  ------------- #

docker stop zd-listen
docker rm zd-listen

docker stop zd-listen2
docker rm zd-listen2

docker stop zd-listen3
docker rm zd-listen3

docker stop zd-validation
docker rm zd-validation


docker stop zd-db
docker rm zd-db


# ------------- Stop and remove the validator containers  ------------- #

docker stop validator-listen
docker rm validator-listen

docker stop validator-publish
docker rm validator-publish



# ------------- Stop and remove the Message Queue containers  ------------- #

docker stop mq
docker rm mq


# ------------- Stop and remove the web interface containers  ------------- #

docker stop interface
docker rm interface


# ------------- Remove the Docker network ------------- #

docker network rm containernetwork