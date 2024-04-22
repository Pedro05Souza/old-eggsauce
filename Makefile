#Setup for unix-based OS
setup-unix: requirements.txt
	./setup.sh

#Setup for Windows OS
setup-windows: requirements.txt
	cmd /C setup.bat


init: build run
.PHONY: init

build:
	docker build -t eggsaucebot .
.PHONY: build

run:
	docker run -p 3300:3300 --name egg_container eggsaucebot
.PHONY: run

clean:
	docker rm --force egg_container
	docker rmi --force eggsaucebot
.PHONY: clean

restart: clean init
.PHONY: restart