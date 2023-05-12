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

### `POST /api/login`<a id="login"></a>

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

### `POST /api/login/refresh`<a id="login-refresh"/>

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

### `GET /api/races/available`

Lists all the races in which user can participate. It doesn't show races which has already started or ended.<br />
_Note: user doesn't have to be logged in to see this list but to participate in any of them he should login first._

**Response:**

* List or races each item of which contains next fields:
  * `id` : 10 characters long unique identifier of the race.
  * `creator` : creator's username.

**Status codes:**

* `200` : success.

### `GET /api/races/race/create`

Creates a new race which will be available to join until the race is started or finished or until it gets deleted, server gets deleted if there are no more players on the server or until server lifetime runs out. [More on the race mechanics...]()<br />
_Note: user has to be logged in to create a new race._

**Response:**

* `id` : 10 characters long unique identifier of the race.
* `creator` : creator's username.

**Status codes:**

* `201` : Race was successfully created.
