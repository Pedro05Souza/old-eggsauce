# BOT Ovomaltine

This is an open source Discord bot project made as personal project by [Alexius Dias](github.com/AlexiusMD) and [Pedro Souza](github.com/Pedro05Souza). This bot's purpose was made for a friends-only server with the intention of gaining points during calls in order to buy custom and default commands, such as ban, kick, momentDeSilencio and many more.

## How to run this repository locally

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

Please note that the `API key` nor the `database.txt` file are **NOT** available for use on the repo, and must be created privately in your local project directory.



## Suggestion
An issue you may encounter with the `.env` file is after you set it up in your project, it may still not recognize it, in order to make our project able to run in your computer, you need to restart your Python Enviroment. If using Visual Studio code `Ctrl+Shift+P` to open the command palette, then type and select `Reload Window`.



