## COMMANDS:

![alt text](image-1.png)

This topic covers all commands currently available in the bot, covering what it can do, explained in simple terms for easy understading, it is important to note that the bot's default prefix is set to `!`. If you have any suggestions feel free to contact us!


## MOD COMMANDS:

This subtopic contains commands that can only be usable by developers working in the bot.


```
addPontos amount, User
```

Gives a determined amount of `eggbux` to the specified user.

```
removePontos amount, User
```

Removes a determined amount of `eggbux` from the specified user

```
deleteDB User
```

Deletes the specified user from the database.

```
removerCargo User role
```
Removes a specific role from the specified user by passing a character, each of them representing one of the four possible roles.

## POINTS COMMANDS:

This subtopic contains all `eggbux` related commands.

```
pontos @Optional User OR verPontos @Optional User
```

Returns the author's points if no User parameter is passed, if passed, returns the user's points.

```
shop
```

Returns a list of all the commands and their respectives prices.

```
leaderboard
```
Returns a list of all the users in the database sorted amount of points.

```
claim
```
This is a situatial command, which will only work when `drop_eggbux` function is called

```
doarPontos User amount
```
Gives the author's selected amount of points to the specified User.

```
roubarPontos User
```
Steals a maximum of 20% of the specified User networth.

## TEXT COMMANDS:

This subtopic contains all the text-related commands.

```
balls
```
Bot types `balls` in the chat.

```
mog User
```
Randomize between 8 images found in `BotDiscord/images`

```
purge amount
```
Deletes a maximum of 25 chat messages.

```
kick User
```
Kicks the specified user from the local guild.

```
ban User
```
Bans the specified user from the local guild.

```
mudarApelido User, new nickname
```
Change the specified user's nickname.

```
perdoar User
```
Unbans the specified user from the local guild.

```
cassino amount color
```
The cassino command has three possible results, red, black that multiplies the amount by two and green which multiplies the given amount by fourteen. The chances are, from 0 to 35:

RED: Below 18
BLACK: Above 18
GREEN: 0


## ROLE COMMANDS:

Those commands are located inside of text commands but they need their own category as they're crucial for the bot's fun. Every role has a salary that is incremented into the user's networth every `1600` seconds. Note: You need to buy them sequentially. So every role's permissions will be accumlated overtime.


```
cargoTrabalhador
```
Gives permission to move members and earns a salary of 50 `eggbux`.

```
cargoClasseBaixa
```
This role comes with the permissions of muting and deafening members and earns a salary of 100 `eggbux`

```
cargoClasseMedia
```
This role comes with the permissions of managing messages and earns a salary of 200 `eggbux`

```
cargoClasseAlta
```
this role comes with the permissions of managing channels and earns a salary of 300 `eggbux`.


## VOICE COMMANDS:
amn eu faço










