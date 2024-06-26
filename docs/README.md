# Eggsauce BOT:

![alt text](image-2.png)

This is an open source Discord bot project made as a personal project by [Alexius Dias](github.com/AlexiusMD) and [Pedro Souza](github.com/Pedro05Souza). This bot's purpose was made for a friends-only server with the intention of gaining a currency named as `eggbux` during calls, the current rate is set at 1 eggbux every 10 seconds of call time. You can use the currency to buy custom an immense amount of commands. If you want to use this bot in your server, it is recommended that every member has the same roles, same permissions so the experience can be as best as the bot can provide. This project has built-in support for MongoDB.

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

Please note that the `API key` and MongoDB database storage are **NOT** available for use on the repo, and must be created privately in your local project directory. To generate your API key, click [here](https://discord.com/developers/applications). Make sure you're logged on to the discord website. Top right of your screen, click `new application`

![alt text](image.png)

Give the application a name and click "Create". Navigate to the `Bot` tab, reset your token and copy it to the clipboard and paste it in the `.env` file. If you do not have a `.env` file in your directory, you should create one. The `.env` file should follow the format in `.env.example`.


## How to run Docker in your machine:

1. Install [Docker Desktop](https://www.docker.com/products/docker-desktop.).

2. After installing docker, verify your installation, open your terminal and run the following command:

```
docker --version
```

3. If sucessful, proceed to build the docker image. Open the terminal and navigate to your project directory and enter the following command. (Remember to switch the `image_name` with a name for your image)

```
docker build -t image_name .
```

4. Once the image is built, you can run a container based on that image using the following command:

```
docker run -p host_port:container_port image_name
```
Replace the `host_port` and `container_port` with the ports you're going to use


## AI Integration:

WIP


## Known Issues (Windows):
This topic is for known issues that happened with this project and a suggestion on how fix each one of them. If you happen to find any more issues that aren't here message the developers and let us know!

An issue you may encounter with the `.env` file is after you set it up in your project, your IDE may still not recognize it, in order to make our project able to run in your computer, you need to restart your Python Enviroment. If using Visual Studio code `Ctrl+Shift+P` to open the command palette, then type and select `Reload Window`.

Another issue that in case you encounter is involving your virtual enviroment. If you try to run `make setup-windows` and for some reason it doesn't locate the 'requirements.txt` file in your directory, it can possible be related to this problem. To fix this you need to first remove the current enviroment. In your powershell terminal, type the following command:

```
rm -r "directorypathhere"
```
If sucessful, recreate the enviroment. 
```
python -m venv venv
```
If sucessful execute the make setup command again.

