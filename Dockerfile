# Start
FROM python:3.6

COPY ./recipe_app /recipe_app

WORKDIR /recipe_app

RUN pip install -r ./requirements.txt

# tell the port number the container should expose
EXPOSE 80

# run the command
CMD python ./app.py
