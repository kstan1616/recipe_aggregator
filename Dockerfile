# Start
FROM python:3.6

COPY ./recipe_app /recipe_app

WORKDIR /recipe_app

RUN pip install -r ./requirements.txt

# install google chrome
# RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
# RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
# RUN apt-get install -y google-chrome-stable

# install chromedriver
# RUN apt-get install -yqq unzip
# RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip
# RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/

# set display port to avoid crash
ENV DISPLAY=:99

# tell the port number the container should expose
EXPOSE 80
EXPOSE 25
EXPOSE 587

# run the command
CMD python settings.py
CMD python ./app.py
