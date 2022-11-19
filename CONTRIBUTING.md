# CONTRIBUTING GUIDELINES

## Setting up Development Environment

### Clone the repository

```shell
git clone https://github.com/PlayLiveChess/playlivechess-game.git
```

### Create Virtual Environment

If you haven't installed virtualenv, install it before proceeding with further steps:
```shell
sudo apt install python3-virtualenv
```
Now, let's create a virtual environment. Note that you only have to do it once.
```shell
cd playlivechess-game
virtualenv venv
```
Activating virtual environment:
```shell
source venv/bin/activate
```

### Installing redis (Optional)

If you are using redis for working with channel layers, you have to install redis on your system, or switch to in memory channel layers.

```shell
sudo apt install redis
```

### Installing dependencies

```shell
pip3 install -r requirements.txt
```

### Running the server

```
python3 manage.py runserver
```

## Understanding the project structure

`gameserver` app is the core application of this `django` project. It is used for managing the settings, url patterns, etc.

`gamechannels` app is responsible for handling the request for websocket connections to this server.

### Consumers for socket event handling

All the consumers are defined in `gamechannels/consumers.py`. Currently we have just one consumer, which is responsible for handling connectins at route `ws/connect/` (route defined in `gamechannels/routing.py`).

This consumer processes requests from each individual player who is interested in playing a game.

### `QueueThread` for pairing players

Each new player who requests to start a new game, is queued up in `QueueThread`. Players are queued to different buckets according to their ratings. (*Currently, rating functionality is not implemented. Thus, all players are assumed to have a rating of 1000.*) `QueueThread` iterates through all buckets, and pairs up players placed in same bucket. It starts a new game, and sends an event to both the player channels indicating that the game has been started.

### `HealthThread` for maintaining and transmitting health checks

This thread is responsible for maintaining health checks, and update details about the status of the server to master server.