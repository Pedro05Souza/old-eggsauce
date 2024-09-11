![alt text](image.png)

# Eggsauce

This Discord bot project, named Eggsauce, was initially started by [Pedro Souza](https://github.com/Pedro05Souza) with early contributions from [Alexius Dias](https://github.com/AlexiusMD). Currently, the project is maintained and developed solely by Pedro Souza.


##  Project Dependencies

In order to install dependancies, you must first clone the repo onto a directory of your liking. If you're using a Unix-based operating system, you can install the necessary dependencies by crunning the following command in your terminal:
```
make setup-unix
```

For Windows, you must do some additional steps before executing the `Makefile`:
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


## Running the Bot

Important Notice: Certain configuration `files` and `environment variables` have been excluded from this repository for security purposes. To access these, please reach out to the lead developer.

Please note that sharing any provided files or information is strictly prohibited. The bot will **NOT** execute without the correct setup.

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
