# Typeracer Clone Api Documentation

## Overview

This api allows you to make your own copy of Typeracer game. This game is powered by [Websocket protocol](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API) and [JWT authentication](https://jwt.io/).

# Endpoints

## Signup

### `POST /api/signup`

Allows you to create a new user.

**Request body:**

* `username` : name which will be used in races.
* `password` : password which user will be using for authentication. _(Note: password should contain at least 8 characters, can't be entirely numeric, can't be too common)_ 
* `password2` : password that should match the `password` for validation purposes.
* `email` : email which will be associated with user.
* `first_name` : user's first name.
* `last_name` : user's last name.

**Status codes:**

* `201` : user is created successfully.
* `400` : passwords didn't match or password did not pass the validation.

### Example:

```javascript
/* Creating a new user using javascript fetch api. */
fetch('/api/signup/', {
  method: 'POST',
  headers: {
    "Content-Type": "application/json"
  },
  body: JSON.stringify({
    'username':'ApiUser',
    'password':'ApiPass.123',
    'password2':'ApiPass.123',
    'email':'apiuser@apimail.com',
    'first_name':'John',
    'last_name':'Smith'
  })
})
.then(response => {
  if(response.ok) {
    console.log("New user is created!")
  }
})
.catch(err => {
  console.error(err)
})
```

## Authentication

### <a id="login"></a>`POST /api/login`

Sends refresh token and access token to the client in exchange for username and password. Access token is mostly used for authenticating when entering a race.<br/>
_Note: refresh token and access token have their own expiry date on the server so that you can no longer use them. If access token expires you should [refresh it](#login-refresh). If refresh token expires you need to login using auth credentials again._

**Request body:**

* `username` : name which was used when creating a user.
* `password` : password which was used when creating a user.

**Response:**

* `refresh` : generated refresh token.
* `access` : generated access token.

**Status codes:**

* `200` : successfull login.
* `401` : user with such credentials does not exist or wrong password was given.

### <a id="login-refresh"/>`POST /api/login/refresh`

Sends access token to the client in exchange for the refresh token if refresh token hasn't expired.<br/>
_Note: access token is not required to be in headers._

**Request body:**

* `refresh` : refresh token which was previously created by [login](#login) endpoint.

**Response:**

* `access`: newely generated access token.

**Status codes:**

* `200` : success.
* `400` : refresh field in the request body cannot be empty.
* `401` : passwords didn't match or password did not pass the validation.

### `POST /api/logout`

Expires your refresh token so that it could no longer be used for creating new access tokens.<br/>
_Note: acess token is not required to be in headers._

**Request body:**

* `refresh` : refresh token which was previously created by [login](#login) endpoint.

**Status codes:**

* `205` : success. Refresh token has been successfully expired.
* `400` : refresh field in the request body is either expired or invalid or empty.

### Examples:

```javascript
/* obtaining JWT token pair using 
 * username and password credentials. */
fetch('/api/login/', {
  method: 'POST',
  headers: {
    "Content-Type": "application/json"
  },
  body: JSON.stringify({
    'username':'ApiUser', 
    'password':'ApiPass.123',
  })
})
.then(response => {
  if(response.ok) { 
    return response.json()
  } else {
    throw new Error(`Something went wrong, server response status code is ${response.status}`);
  }
})
.then(json_data => {
  localStorage.setItem('jwt-refresh', json_data['refresh'])
  sessionStorage.setItem('jwt-access', json_data['access'])
})
.catch(err => {
  console.error(err)
})
```

## Races

### <a id="available-races" />`GET /api/races/available`

Lists all the races in which user can participate. It doesn't show races which has already started or ended.<br />
_Note: user doesn't have to be logged in to see this list but to participate in any of them he should login first._

**Response:**

* List or races each item of which contains next fields:
  * `id` : 10 characters long unique identifier of the race.
  * `creator` : creator's username.

**Status codes:**

* `200` : success.

### `POST /api/races/race/create`

Creates a new race which will be available to join until the race is started or finished or until it gets deleted, server gets deleted if there are no more players on the server or until server lifetime runs out. [More on how race is organised...](#race-mechanics)<br />
_Note: user has to be logged in to create a new race._

**Response:**

* `id` : 10 characters long unique identifier of the race.
* `creator` : creator's username.

**Status codes:**

* `201` : Race was successfully created.

# <a id="race-mechanics">Race server/game powered by Websocket</a>

## Workflow

1. First users connects to the server using corresponding websocket route with [race_id](#available-races) and [access_token](#login):
    <pre>/ws/race/<b>race_id</b>/?token=<b>access_token</b></pre>

2. Every time someone connects or disconnects every user including the one who have just connected receives message with a type of `player_list`:
    ```json
    {
      "type": "player_list",
      "players": [
        // there can be multiple of player objects
        {
          "id": 1,
          "username": "ExampleUser"
        }
      ],
      "time": "2018-12-10T13:49:51.141Z" // time when the race will start
    }
    ```
3. There are 2 ways to start the race:
    1. Race start automatically once there are 3 players. When there are 3 players server will send a `player_list` again to indicate when will race start in the `time` field. For the automatic race start it takes **10 seconds** for a race to start. ___When timer is active users can still join.___ Once the timer is up no one can join.
    2. Force start race(this feature is only available to the creator of the race). For force start race it takes **5 seconds** for a race to start. To do so creator of the race should send the following message to the server:
        ```json
        {
          "type": "race_action",
          "action": "start_race"
        }
        ```
4. Once the timer is up every player will get message from the server which will contain the quote that everyone will be typing and also indicates that the race has been started. No players can join anymore and the race is not showing in the [list of available races](#available-races). Quote for the race is randomly chosen from the database of quotes. This message will look like this:
    ```json
    {
      "type": "race_start",
      "quote": "Example quote!", 
      "author": "Jim Smith",
      "categories": [
        // can contain multiple categories
        // which will be looking something like that
        "entertaining"
      ]
    }
    ```
5. To progress in the race client-side application must send every word that is in the quote one by one to the server. This makes it so that every player could see your progress and vise versa you could see every person's progress. Let's look at the following example:
    ```json
    {
      "type": "race_start",
      "quote": "Self-respect permeates every aspect of your life.",
      "author": "Joe Clark",
      "categories": [
        "life"
      ]
    }
    ```
    The above json object is the response server gave all the participants of the race. Every time, participant types a word you must send it to the server as the following kind of object:
    ```json
    {
      "type": "race_progress",
      "word": "Self-respect" // with no leading and trailing whitespaces, otherwise progress won't be caught
    }
    ```
    The server will then check if the word you sent was correct and sent in the right order. If all the conditions are met, every participant will receive the following json response:
    ```json
    {
      "type": "race_progress",
      "user_id": 1, // That's an ID of a user who sent this word
      "word": "Self-respect"
    }
    ```
    Next word you'll be sending will look like this:
    ```json
    {
      "type": "race_progress",
      "word": "permeates"
    }
    ```
    So on and so forth, after sending the last word to the server. Then server will count the time you spent on the race and will record it to the database. When one participant finishes, the race will be automatically marked as finished inside the database, which means the race won't be deleted(database record deletion is only applied for innactive servers).