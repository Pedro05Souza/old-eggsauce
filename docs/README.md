# Eggsauce BOT:

![alt text](image-2.png)

This is a Discord bot project made as a personal project by  [Pedro Souza](github.com/Pedro05Souza). With time to time contributions from [Alexius Dias](github.com/AlexiusMD).

## How to run this repository locally:

In order to run this repository locally, you must first clone the repo onto a directory of your liking. If your OS is Unix-based, you can just run the following command on the terminal:
```
make setup-unix
```

If your OS is Windows, you must do some additional steps before running the `Makefile`
- Install the [chocolatey package manager](https://chocolatey.org/install) 
- Run the following command in your windows powershell terminal:
```
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```
- After running sucessfully, run the following command to install the make path to all CLI on your OS:

```
choco install make
```

Then, finally you can run the following command to run the application setup:

```
make setup-windows
```

Both the setup commands run the `Makefile` and:
* Creates the python virtual enviroment (venv)
* Installs all dependencies listed on `requirements.txt`


## How to run Docker in your machine:

1. Install [Docker Desktop](https://www.docker.com/products/docker-desktop.).

2. After installing docker, verify your installation, open your terminal and run the following command:

```
docker --version
```

3. If sucessful, proceed to build and run with docker-compose entering the following command:

```
make build
```

