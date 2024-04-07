# BOT Ovomaltine:

This is an open source Discord bot project made as a personal project by [Alexius Dias](github.com/AlexiusMD) and [Pedro Souza](github.com/Pedro05Souza). This bot's purpose was made for a friends-only server with the intention of gaining a currency named as `eggbux` during calls in order to buy custom and default commands, such as ban, kick, momentDeSilencio and many more. At the current moment the rate of eggbux is one per five seconds of call time.

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

Please note that the `API key` nor the `database.txt` file are **NOT** available for use on the repo, and must be created privately in your local project directory.



## Suggestion:
An issue you may encounter with the `.env` file is after you set it up in your project, it may still not recognize it, in order to make our project able to run in your computer, you need to restart your Python Enviroment. If using Visual Studio code `Ctrl+Shift+P` to open the command palette, then type and select `Reload Window`.

## Commands:
For informational purposes, every command starts with `!`, so in this list, it will be implicity used.

```
mog
```
As the name itself says, it randomizes between 8 images present in the project, you can find them at: `images/mogged`.

```
mute @User
```
Self-explanatory.

```
ChangeNickname @User @NICKNAME_HERE
```
Self-explanatory.

```
purge @amount
```
Deletes messages from the chat. The limit for safety reasons is currently set at `25`.

```
kick @User
```
Self-explanatory.

```
ban @User
```
Self-explanatory.

```
Pardon @User
```
self-explanatory.

```
momentDeSilencio
```
Mutes every single user in every call in the server.

```
god
```
If you apply this command in yourself, it's impossible for any user to mute/deafen you.

```
pontos
```
Returns back how much eggbux the user has accumulated.


```
leaderboard
```
Returns back the whole user-list saved in the `database.txt` file and sort them by descending.

```
shop
```
Essentially shows every single command there is and their eggbux price.
