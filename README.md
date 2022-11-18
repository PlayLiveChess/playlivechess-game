# playlivechess-gameserver

## Setting up the project
Read instructions provided in [CONTRIBUTING.md](CONTRIBUTING.md).

## Communicating with the server

### Establish a connection with the server

Send a request at `ws://{deployment_address}/ws/connect/`. This will open up a websocket connection with the server.

The server uses `json` formatting for communcation. Thus, all further communication would be through an exchange of `json` objects. All the message have one mandatory field: `type`. Often, it is accompanied with another field `value`. Additional fields might also be used if needed.

### Queuing

Now, to enter the waiting queue and get paired against an opponent of similar strength, send a queuing message:
```json
{
    "type": "queue"
}
```

#### Response:

All the response messages have `type` set as `reply`. Also, they have a mandatory field `success` indicating failure / success of the request. In case `success` field is `false`, additional field `value` is supplied telling the reason of teh failure.

```json
{
    "type": "reply",
    "success": "true"
}
```

In case of failure:
```json
{
    "type": "reply",
    "success": "false",
    "value": "Already in queue!"
}
```

### Game start response

Once you have been added the queue, another response will be sent when the game has been started.

Response after successful pairing:
```json
{
    "type": "start",
    "color": "white"
}
```

### Playing a move

If it's your turn, you can play a move by sending a `move` request:
```json
{
    "type": "move",
    "value": "e2"
}
```

A reponse will generated for your move.

Successful move:
```json
{
    "type": "reply",
    "success": "true"
}
```

In case the request is rejected, `value` can have different values like `Game has not started yet!`, `Not your turn!`, `Invalid move!`, etc.
```json
{
    "type": "reply",
    "success": "false",
    "value": "Not your turn!"
}
```

If your move has resulted in termination of the game (`checkmate` or `draw`), the response will have additional field `outcome`. In case of a win, additional field `winner` telling the winning color will be given.

Refer this [doc](https://python-chess.readthedocs.io/en/latest/core.html#chess.Termination) for `termination` values.

Reponse in case of win:
```json
{
    "type": "reply",
    "success": "true",
    "outcome": {
        "termination": "1",
        "result": "1-0",
        "winner": "white"
    }
}
```

In case of a draw:
```json
{
    "type": "reply",
    "success": "true",
    "outcome": {
        "termination": "3",
        "result": "1/2-1/2",
    }
}
```

### Opponent move
Whenever opponent plays a move, player gets a message in this format:

```json
{
    "type": "opponent",
    "value": "e4"
}
```

If opponent's move has led to termination of the game, a similar `outcome` field is added.

In case of win (opponent has won):
```json
{
    "type": "opponent",
    "value": "Qxf7",
    "outcome": {
        "termination": "1",
        "result": "1-0",
        "winner": "white"
    }
}
```

### Offer Draw

To be added.

### Resign

To be added

### Game termination

Once the game is terminated, the players can start a new game by sending a `queue` request again to the server.
