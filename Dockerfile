FROM python:3 AS base

# Set common env variable
ARG HOME_DIR="/home/app"
ENV HOME_DIR=${HOME_DIR}

WORKDIR ${HOME_DIR}

# Copy everything from the current directory to the
# PWD(Present Working Directory) inside the container

RUN apt-get update && apt-get -y install cmake libgl1-mesa-glx
COPY src .


RUN pip install -r requirements.txt

EXPOSE 5000

ENTRYPOINT [ "python" ]
CMD [ "app.py" ]
# docker build -t morph_server:latest .