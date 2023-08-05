# build the rabbit mq image
docker build --no-cache --rm -f "..\mq\Dockerfile" -t mq:latest "..\..\"



# build the eplf database image
docker build --no-cache --rm -f "..\db\eplf\Dockerfile" -t eplf-db:latest "..\..\"

# build the elpf fill database image
docker build --no-cache --rm -f "..\db\fill\Dockerfile" -t fill:latest "..\..\"

# build the eplf service images
docker build --no-cache --rm -f "..\eplf\publish\Dockerfile" -t eplf-publish:latest "..\..\"
docker build --no-cache --rm -f "..\eplf\listen\Dockerfile" -t eplf-listen:latest "..\..\"
docker build --no-cache --rm -f "..\eplf\republish\Dockerfile" -t eplf-republish:latest "..\..\"



# build the zd database image
docker build --no-cache --rm -f "..\db\zd\Dockerfile" -t zd-db:latest "..\..\"

# build the zd service image
docker build --no-cache --rm -f "..\zd\Dockerfile" -t zd:latest "..\..\"


# build the web interface
docker build --no-cache --rm -f "..\interface\Dockerfile" -t interface-base:latest "..\..\"
docker build --no-cache --rm -f "..\interface\Dockerfile2" -t interface:latest "..\..\"