# BOT Ovomaltine:

This is an open source Discord bot project made as a personal project by [Alexius Dias](github.com/AlexiusMD) and [Pedro Souza](github.com/Pedro05Souza). This bot's purpose was made for a friends-only server with the intention of gaining a currency named as `eggbux` during calls in order to buy custom and default commands, such as ban, kick, momentDeSilencio and many more. At the current moment the rate of eggbux is one per ten seconds of call time. If you want to use this bot in your server, it is recommended that every member has the same roles, same permissions so the experience can be as best as the bot can provide. This project has built-in support for MongoDB.

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

Please note that the `API key` and MongoDB database storage are **NOT** available for use on the repo, and must be created privately in your local project directory.



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

## Commands:
For informational purposes, every command starts with `!`, so in this list, it will be implicity used.

```
mog
```
As the name itself says, it randomizes between 8 images present in the project, you can find them at: `images/mogged`.

```
mute @User
```
Mutes the user who tagged.

```
mudarApelido @User NICKNAME_HERE
```
Change the nickname of the user.

```
purge @amount
```
Deletes messages from the chat. The limit for safety reasons is currently set at `25`.

```
kick @User
```
Kick the user.

```
ban @User
```
Bans the user.

```
Pardon @User
```
Unbans the user.

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
Returns back the whole user-list saved in MongoDB and sort them by descending.

```
shop
```
Essentially shows every single command there is and their eggbux price.
