FROM postgres:latest

ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=postgres
ENV POSTGRES_DB=db

COPY ./concept_1/db/eplf/init.sql /docker-entrypoint-initdb.d/
