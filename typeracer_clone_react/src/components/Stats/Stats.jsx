import React, { useState, useContext, useEffect } from 'react'
import { UserContext } from '../../App';
import { Avatar, List, ListItem, ListItemAvatar, ListItemText, ListSubheader, Typography, Divider, Paper, Box } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import ListItemWithHover from './ListItemWithHover';


function Stats() {
  const {isLoggedIn} = useContext(UserContext)
  const [userInfo, setUserInfo] = useState("")
  const [quoteIndex, setQuoteIndex] = useState(0)

  const location = useNavigate()
  
  useEffect(() => {
    if(!isLoggedIn) {
        location('/singin')
        return
    }

    const statLogic = async () => {
      let access_token = await fetch('/api/login/refresh/', {
        method: 'POST',
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({refresh: localStorage.getItem('jwt-refresh')}),
      })
      .then(response => {
        if(response.ok) { 
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
        

    await fetch('/api/stats/', {
        method: 'GET',
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${sessionStorage.getItem('jwt-access')}`
        },
      })
    .then((res) => res.json())
    .then((data) => {
        console.log(data);
        setUserInfo(data);
    })
    .catch((err) => {
        console.log(err.message);
    });
    }

    statLogic()
  }, []);



  return (
    <>
      {userInfo
      &&
      <>
      <Box sx={{width: '100%', display: 'flex', p: 2, alignItems: 'baseline'/*height: '100vh'*/}}>
      <List
        sx={{ width: '100%', maxHeight: 600,  maxWidth: 600, bgcolor: 'background.paper', borderColor: 'rgba(0, 0, 0, 0.12)', borderWidth: 1, borderStyle: 'solid', overflowY: 'revert', overflowX: 'hidden' }}
        subheader={
            <>
              <ListSubheader sx={{  /*display: 'flex', justifyContent: 'space-between'*/}}> 
                {userInfo["username"]}
                <Divider sx={{ml: -2, mr: -2}}/>
              </ListSubheader>
            </>
          }
      >
        {userInfo.races_statistics.map((raceStats, idx) => <ListItemWithHover setQuoteIndex={setQuoteIndex} raceStats={raceStats} key={idx} idx={idx} />)}
     
      </List>
      <Paper variant="outlined" sx={{zIndex: 10, height: 'auto', width: 500, p: 2, ml: '4%', position: 'relative', top: '2rem'}}><Typography><b>Quote:</b> {userInfo.races_statistics[quoteIndex].race.quote.quote}</Typography></Paper>
      </Box>
      </>}
    </>
  )
}

export default Stats