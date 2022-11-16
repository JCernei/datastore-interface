FROM python:slim
RUN pip3 --no-input install Flask requests
ADD . .
EXPOSE 8080-8082
CMD [ "python3", "cluster_server", "8080"]
