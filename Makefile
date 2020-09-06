init:
	virtualenv -p python3 venv

install:
	pypy3 -m pip install -r requirements.txt

build-docker:
	docker build -t yomolify/backtrader .

run:
	docker run -ti -v`pwd`:/app -d -e ENVIRONMENT=production vulcan