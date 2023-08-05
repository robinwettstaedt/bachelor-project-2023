# Use the official RabbitMQ image from the Docker Hub
FROM rabbitmq:3.12-management

# Enable RabbitMQ plugins (here the management plugin is enabled)
RUN rabbitmq-plugins enable --offline rabbitmq_management

# Set the environment variables (Replace 'your_user' and 'your_password' with your desired user and password)
ENV RABBITMQ_DEFAULT_USER=rabbit
ENV RABBITMQ_DEFAULT_PASS=rabbit
ENV RABBITMQ_HEARTBEAT=0

# Include the configuration file
COPY ./concept_1/mq/rabbitmq.conf /etc/rabbitmq/

# Expose ports
# 5672: used by AMQP 0-9-1 and 1.0 clients without and with TLS
# 15672: used by HTTP API clients, RabbitMQ management UI and RabbitMQ Prometheus exporter
EXPOSE 5672 15672

# Set the entrypoint
ENTRYPOINT ["rabbitmq-server"]
