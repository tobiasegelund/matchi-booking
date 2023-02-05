build:
		docker build -t matchi .

it:
		docker run -it --rm matchi bash

run:
		docker run --rm matchi main.py

script:
		python3 main.py

tar:
		tar -czf matchi.tar.gz Dockerfile main.py requirements.txt README.md chromedriver
