# pull official base image
FROM python:3.8.10

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt

# copy entrypoint.sh
COPY ./entrypoint.sh /usr/src/app/entrypoint.sh

# copy project
COPY . /usr/src/app/

# copy environment file .env
# COPY ./.env /usr/src/app/x.env

# run entrypoint.sh
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
