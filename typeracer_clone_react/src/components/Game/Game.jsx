import { Paper, Button, Card, CardActions, CardContent, CardMedia, TextField, Typography, Box, FormControl, Divider, withTheme } from '@mui/material'
import React, { useEffect, useState, useContext, useRef } from 'react'
import { useParams, useLocation } from 'react-router-dom';
import { useFormControl } from '@mui/material/FormControl';
import "./disable_copy.css"
import PedalBikeOutlinedIcon from '@mui/icons-material/PedalBikeOutlined';
import DirectionsRunOutlinedIcon from '@mui/icons-material/DirectionsRun';
import AirportShuttleOutlinedIcon from '@mui/icons-material/AirportShuttle';
import { useWebSocket } from 'react-use-websocket/dist/lib/use-websocket';
import { UserContext } from '../../App';
import RequiresLogin from '../RequiresLogin/RequiresLogin'
import jwt_decode from "jwt-decode";
import { useNavigate } from 'react-router-dom';


function Game() {
  let { game_id, creator_id } = useParams();
  const [gameLink, setGameLink] = useState('')
  const socket = useRef();

  const { isLoggedIn } = useContext(UserContext)
  const [gameText, setGameText] = useState("")
  const [gameTextForDisplay, setGameTextForDisplay] = useState("")
  const [typedTextToThatPoint, setTypedTextToThatPoint] = useState('')
  const [typedCharacters, setTypedCharacters] = useState('')
  const [correctlyTypedCharactersIdx, setCorrectlyTypedCharactersIdx] = useState(0)

  const [playerList, setPlayerList] = useState([])
  const playerListRef = useRef([]);
  playerListRef.current = playerList
  const [colors, setColors] = useState([])
  const [startDate, setStartDate] = useState()

  const [isTypingAllowed, setIsTypingAllowed] = useState(false)

  const [thisUserId, setThisUserId] = useState(NaN)
  const [serverExists, setServerExists] = useState(true)

  const location = useNavigate()
  const vehicleLooksArray = ['b', 'c', 'p']


  const generateRandomColorAsRgbString = () => {
    return "rgb(" + Math.floor(Math.random() * 255)
      + "," + Math.floor(Math.random() * 255) + ","
      + Math.floor(Math.random() * 255) + ")"
  }

  const processMessage = (event) => {
    console.log(event)
    let data = event.data
    console.log(typeof data)
    data = JSON.parse(data)
    switch (data["type"]) {
      case "player_list":
        let players = data["players"]
        console.log(players[0])

        let new_playerList = []

        for (let i = 0; i < players.length; ++i) {
          let indexInOldArray = playerListRef.current.findIndex(player => player["id"] === players[i]["id"])

          if (indexInOldArray === -1) {
            console.log("A new person has entered the room!!!")
            let new_player = players[i];
            new_player["word_index"] = 0;
            new_player["color"] = generateRandomColorAsRgbString()
            new_player["place"] = undefined
            new_player["finishing_time"] = undefined
            new_player["average_speed"] = undefined

            new_playerList.push(new_player)

          } else {
            console.log("Just some old people here")
            new_playerList.push(playerListRef.current[indexInOldArray])
          }
        }

        setPlayerList(new_playerList)
        console.log(new_playerList)

        if (Object.hasOwn(data, "time")) {
          setStartDate(Date.parse(data["time"]))
        }

        break;

      case "race_start":
        let quote = data["quote"]
        setGameText(quote)
        setGameTextForDisplay(quote)
        setIsTypingAllowed(true)
        break;

      case "race_progress":
        let player_id = data["player_id"]
        let word_index = data["word_index"]

        let index = playerListRef.current.findIndex(player => player["id"] === player_id)

        playerListRef.current[index]["word_index"] = word_index + 1
        setPlayerList([...playerListRef.current])

        break;

      case "race_player_finished":
        let finished_player_id = data["player_id"]
        let time_racing = data["time_racing"]
        let place = data["place"]
        let average_speed = data["average_speed"]

        let finishedPlayerIndex = playerListRef.current.findIndex(player => player["id"] === finished_player_id)

        playerListRef.current[finishedPlayerIndex]["place"] = place
        playerListRef.current[finishedPlayerIndex]["finishing_time"] = time_racing
        playerListRef.current[finishedPlayerIndex]["average_speed"] = average_speed
        setPlayerList([...playerListRef.current])

        setIsTypingAllowed(false)
        break;

      case "update_vehicle_look":
        let playerIndex = playerListRef.current.findIndex(player => player["id"] === data["player_id"])
        playerListRef.current[playerIndex]["vehicle_look"] = data["vehicle_look"]
        setPlayerList([...playerListRef.current])

        break;
    }
  }

  const getAccessToken = async () => {
    console.log("Creating new access token")
    let access_token = await fetch('/api/login/refresh/', {
      method: 'POST',
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ refresh: localStorage.getItem('jwt-refresh') }),
    })
      .then(response => {
        if (response.ok) {
          return response.json();
        } else {
          throw new Error(`Something went wrong, server response status code is ${response.status}`);
        }
      })
      .then(json_data => {
        return json_data['access'];
      })
      .catch(err => {
        console.error(err)
      })

    sessionStorage.setItem('jwt-access', access_token)

    return access_token
  }

  useEffect(() => {
    (async () => {
      let token = await getAccessToken()
      let gameLinkToBeSet = `/ws/race/${game_id}/?token=${token}`
      setGameLink(gameLinkToBeSet)
      let decodedToken = jwt_decode(token)
      setThisUserId(decodedToken['user_id'])
      let tempSocket = new WebSocket("ws://" + "127.0.0.1:8000" /* window.location.hostname*/ + gameLinkToBeSet)
      socket.current = tempSocket
      tempSocket.addEventListener("message", (event) => {
        processMessage(event)
      })
      tempSocket.addEventListener("close", () => {
        setServerExists(false)
      })
    }
    )()
  }, [game_id]);

  //const { sendJsonMessage, lastMessage, readyState, getWebSocket } = useWebSocket(
  //	"ws://" + "127.0.0.1:8000" /* window.location.hostname*/ + gameLink,
  //	{
  //		onMessage: (event) => { processMessage(event) },
  //		onClose: (event) => { gameLink !== '' ? setServerExists(false) : console.log("link is empty"), console.log("connection closed") },
  //		//share: true,
  //	})

  const handlePaste = (event) => {
    event.preventDefault();
  }

  const changeCurrentTypedCharacters = (chars) => {
    setTypedCharacters(chars)
  }

  const compareAndFindWrongIndex = (string1, string2) => {
    for (let i = 0; i < string1.length; ++i) {
      if (string1[i] != string2[i]) {
        return [false, i]
      }
    }
    return [true, null]
  }

  const gameControlFunc = (event) => {
    changeCurrentTypedCharacters(event.target.value)
    let temp_typedTextToThatPoint = typedTextToThatPoint + event.target.value
    let temp_typedTextToThatPointLength = temp_typedTextToThatPoint.length
    let [isCorrect, index] = compareAndFindWrongIndex(gameText.slice(0, temp_typedTextToThatPointLength), temp_typedTextToThatPoint)
    console.log('I"m here')
    if (!isCorrect) {
      console.log("You typed wrong character")
      setGameTextForDisplay("<span class=\"green\">" + gameText.slice(0, index) + "</span><span class=\"red\">" + gameText.slice(index, temp_typedTextToThatPointLength) + "</span>" + gameText.slice(temp_typedTextToThatPointLength))
      setCorrectlyTypedCharactersIdx(index)
    } else {
      console.log("You type correct characters")
      setGameTextForDisplay("<span class=\"green\">" + gameText.slice(0, temp_typedTextToThatPointLength) + "</span>" + gameText.slice(temp_typedTextToThatPointLength))
      if (temp_typedTextToThatPoint[temp_typedTextToThatPointLength - 1] === ' ' || ((temp_typedTextToThatPoint[temp_typedTextToThatPointLength - 1] === gameText[temp_typedTextToThatPointLength - 1]) && temp_typedTextToThatPointLength === gameText.length)) {
        socket.current.send(JSON.stringify({
          "type": "race_progress",
          "word": (event.target.value).trim()
        }))
        setTypedTextToThatPoint(temp_typedTextToThatPoint)
        setTypedCharacters('')
        console.log(`Progress being sent: ${JSON.stringify({
          "type": "race_progress",
          "word": (event.target.value).trim()
        })}`)
      }
      setCorrectlyTypedCharactersIdx(temp_typedTextToThatPointLength)
    }
  }

  const calculateProgress = (player) => {
    return player["word_index"] / gameText.split(' ').length
  }

  const startGame = () => {
    socket.current.send(
      JSON.stringify({
        "type": "race_action",
        "action": "start_race"
      })
    )
  }

  const updateVehicleLook = (look) => {
    socket.current.send(
      JSON.stringify({
        "type": "race_action",
        "action": "change_vehicle_look",
        "vehicle_look": look,
      })
    )
  }

  const finishing_time_parser = (finishing_time) => {
    let time_without_ms = finishing_time.split(".")[0];
    let time_array = time_without_ms.split(":")

    return parseInt(time_array[0]) * 3600 + parseInt(time_array[1]) * 60 + parseInt(time_array[2])

  }

  const determinePlayersVehicle = (player) => {
    if (player["vehicle_look"] === 'c') {
      return <AirportShuttleOutlinedIcon fontSize='large' sx={{ color: player["color"] }} />
    } else if (player["vehicle_look"] === 'p') {
      return <DirectionsRunOutlinedIcon fontSize='large' sx={{ color: player["color"] }} />
    } else {
      return <PedalBikeOutlinedIcon fontSize='large' sx={{ color: player["color"] }} />
    }
  }

  return (
    (serverExists)
      ?
      <>
        <Box sx={{ height: '100%', width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', }}>
          <Paper variant='outlined' sx={{ maxHeight: 600, maxWidth: 900, height: '100%', width: '100%', p: 3, display: 'flex', flexDirection: 'column', justifyContent: 'flex-end' }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Box>{gameText ? "" : <Typography>{startDate ? `Game will start in ${Math.round((startDate - Date.now()) / 1000)} s` : "Waiting for players..."}</Typography>}</Box>
              <Box>{!startDate ? (thisUserId === parseInt(creator_id)) ?
                <Button
                  //size='small'
                  variant="outlined"
                  // variant="contained"
                  //sx={{ mt: 2, mb: 2 }}
                  onClick={startGame}
                >
                  Start game
                </Button> : ""
                : ""}
              </Box>
            </Box>
            <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%', justifyContent: 'center' }}>

              {playerList.map(function(player) {
                return (
                  <Box key={player.id}>
                    <Box sx={{ display: 'flex', flexDirection: 'column', mt: 3 }}>
                      <Box sx={{}}>
                        <Typography sx={{ color: 'text.secondary' }}>{player.username}</Typography>
                      </Box>
                      <Box sx={{ display: 'flex', width: '100%' }}>
                        <Box sx={{ width: `${calculateProgress(player) * 100}%`, transition: "width 1s", display: 'flex', justifyContent: 'space-around' }}>
                          {player["place"]
                            ?
                            <>
                              <Box><Typography sx={{ color: 'text.disabled' }}>Place: {player["place"]}</Typography></Box>
                              <Box><Typography sx={{ color: 'text.disabled' }}>Time: {finishing_time_parser(player["finishing_time"])}  s</Typography></Box>
                              <Box><Typography sx={{ color: 'text.disabled' }}>Speed: {Math.floor(player["average_speed"] * 60)} chars/min</Typography></Box>
                            </>
                            :
                            ""
                          }</Box>
                        {determinePlayersVehicle(player)}
                      </Box>
                    </Box>
                    <Divider />
                  </Box>
                )
              })}


            </Box>
            <Paper variant='outlined' sx={{ p: 2, mt: 5 }}><Typography dangerouslySetInnerHTML={{ __html: gameTextForDisplay }} /></Paper>
            <FormControl>
              <TextField fullWidth id="standard-basic" label="Type here" variant="outlined" sx={{ mt: 2 }} onChange={gameControlFunc} onPaste={handlePaste} value={typedCharacters} />
            </FormControl>
          </Paper>
          <Box sx={{ maxHeight: 600, height: '100%', width: '40px' }}>
            {startDate ? '' : vehicleLooksArray.map((l) => {
              return (
                <Box>
                  <Button vairant='outlined' onClick={() => updateVehicleLook(l)}>{l}</Button>
                </Box>
              )
            })}
          </Box>
        </Box>
      </>
      :
      <RequiresLogin />

  )
}

export default Game
