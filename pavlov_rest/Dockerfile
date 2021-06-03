FROM python:3.7.9-stretch

COPY ./bert_mult/web /web
RUN mkdir -p /saved_models
RUN mkdir -p /current_model

# Install curl
RUN apt-get update && apt-get install -y \
  curl \
  && rm -rf /var/lib/apt/lists/*

# Install docker client    
ENV DOCKER_CHANNEL stable
ENV DOCKER_VERSION 20.10.6
ENV DOCKER_API_VERSION 1.41
RUN curl -fsSL "https://download.docker.com/linux/static/${DOCKER_CHANNEL}/x86_64/docker-${DOCKER_VERSION}.tgz" \
  | tar -xzC /usr/local/bin --strip=1 docker/docker

RUN python -m pip install -r /web/requirements.txt

CMD ["python", "/web/runner.py", "runserver", "--host", "0.0.0.0", "--port", "5000"]