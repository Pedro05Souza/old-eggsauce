<div align="center">
    <img src="image-1.png" alt="Logo" width="200" height="200">
    <h3 align="center">Eggsauce</h3>
</div>

<details>
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#maintainability">Maintainability</a></li>
    <li><a href="#built-with">Built With</a></li>
    <li><a href="#project-dependencies">Project Dependencies</a></li>
    <li><a href="#running-the-bot">Running the Bot</a></li>
    <li><a href="#troubleshooting-and-support">Troubleshooting and Support</a></li>
  </ol>
</details>

# Maintainability

This Discord bot project, named Eggsauce, was initially started by [Pedro Souza](https://github.com/Pedro05Souza) with early contributions from [Alexius Dias](https://github.com/AlexiusMD). Currently, this version of the project is deprecated and the bot's development will continue privately.

## Built With

Here are the main technologies and dependencies used in this project:

![Static Badge](https://img.shields.io/badge/discord.py-7289DA?style=for-the-badge&logo=discord&logoColor=white)
![Static Badge](https://img.shields.io/badge/MongoDB%20(Motor)-47a248?style=for-the-badge&logo=mongodb&logoColor=white)
![Static Badge](https://img.shields.io/badge/numpy-blue?style=for-the-badge&logo=numpy)


## Project Dependencies

To install dependencies, you must first clone the repo onto a directory of your choice. If you're using a Unix-based operating system, you can install the necessary dependencies by running the following command in your terminal:

```powershell
make setup-unix
```

For Windows, you must do some additional steps before executing the `Makefile`:
- Install the [chocolatey package manager](https://chocolatey.org/install) 
- Run the following command in your windows powershell terminal:
```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```
- After running sucessfully, run the following command to install the make path to all CLI on your OS:

```powershell
choco install make
```

Then, finally you can run the following command to run the application setup:

```powershell
make setup-windows
```

Both the setup commands run the `Makefile` and:
* Creates the python virtual enviroment (venv)
* Installs all dependencies listed on `requirements.txt`

## Running the Bot

Important Notice: Certain configuration `files` and `environment variables` have been excluded from this repository for security purposes. To access these, please reach out to the lead developer.

Please note that sharing any provided files is **strictly** prohibited. The bot will **NOT** execute without the correct setup.

1. Install [Docker Desktop](https://www.docker.com/products/docker-desktop.).

2. After installation, confirm Docker is correctly set up by running the following command in your terminal:

```powershell
docker --version
```

3. If Docker is successfully installed, you can proceed by building and running the project using `docker-compose`. Execute the following command:

```powershell
make build
```

## Troubleshooting and Support

If you encounter any difficulties running the project or have questions, please do not hesitate to contact the lead developer. 
