FROM python:3.10.9-slim-buster

RUN apt-get update \
	&& apt-get install -y xvfb gnupg wget curl unzip cron --no-install-recommends \
	&& wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
	&& echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
	&& apt-get update -y \
	&& apt-get install -y google-chrome-stable \
	&& CHROMEVER=$(google-chrome --product-version | grep -o "[^\.]*\.[^\.]*\.[^\.]*") \
	&& DRIVERVER=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROMEVER") \
	&& wget -q --continue -P /chromedriver "http://chromedriver.storage.googleapis.com/$DRIVERVER/chromedriver_linux64.zip" \
	&& unzip /chromedriver/chromedriver* -d /chromedriver


RUN chmod +x /chromedriver/chromedriver \
	&& mv /chromedriver/chromedriver /usr/bin/chromedriver

WORKDIR /run

ENV DISPLAY=:99

COPY main.py requirements.txt .env .

RUN pip install pip -U \
	&& pip install -r requirements.txt --no-cache
	
CMD [ "python3", "main.py" ]
