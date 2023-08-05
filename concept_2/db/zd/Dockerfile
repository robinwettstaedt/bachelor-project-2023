FROM postgres:latest

ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=postgres
ENV POSTGRES_DB=db

COPY ./concept_2/db/zd/init.sql /docker-entrypoint-initdb.d/
