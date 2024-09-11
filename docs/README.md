# Eggsauce BOT

<div style="text-align: center;">
  <img src="image.png" alt="alt text">
</div>

This is a Discord bot project made as a personal project by  [Pedro Souza](github.com/Pedro05Souza). With time to time contributions from [Alexius Dias](github.com/AlexiusMD).

## How to install the repository's dependancies

In order to install dependancies, you must first clone the repo onto a directory of your liking. If your OS is Unix-based, you can just run the following command on the terminal:
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


## How to run this project in your machine

Before proceeding, ensure you have the necessary project folder with all required configurations. Please contact the lead developer to obtain it.

1. Install [Docker Desktop](https://www.docker.com/products/docker-desktop.).

2. After installation, confirm Docker is correctly set up by running the following command in your terminal:

```
docker --version
```

3. If Docker is successfully installed, you can proceed by building and running the project using `docker-compose`. Execute the following command:

```
make build
```

## Troubleshooting and Support

If you encounter any difficulties running the project or have questions, please do not hesitate to contact the lead developer. 
[Pedro Souza] (github.com/Pedro05Souza)
