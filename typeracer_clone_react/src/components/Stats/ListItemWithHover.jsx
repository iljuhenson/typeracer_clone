import React, {useState} from 'react'
import VideogameAssetOutlinedIcon from '@mui/icons-material/VideogameAssetOutlined';

import { Avatar, ListItem, ListItemAvatar, ListItemText, Paper, Typography } from '@mui/material';

const ListItemWithHover = ({setQuoteIndex, idx, raceStats}) => {
  const [show, setShow] = useState(false);
  
  
  const finishing_time_parser = (finishing_time) => {
    let time_without_ms = finishing_time.split(".")[0];
    let time_array = time_without_ms.split(":")

    return parseInt(time_array[0]) * 3600 + parseInt(time_array[1]) * 60 + parseInt(time_array[2])
  }
        
  return (
    <ListItem
      sx={{position: 'static', cursor: 'pointer', width: '100%'}}
      onMouseOver={() => setQuoteIndex(idx)}
      //onMouseOut={() => setShow(false)}
      
      divider
    >
      <ListItemAvatar>
        <Avatar size="small">
            {raceStats["place"]}
        </Avatar>
        </ListItemAvatar>
      <ListItemText primary={`${Math.floor(raceStats["average_speed"] * 60)} chars/min`} /*secondary={`Time: ${finishing_time_parser(raceStats["time_racing"])} s`}*/ />
      <ListItemText secondary={`Time: ${finishing_time_parser(raceStats["time_racing"])} s`} sx={{textAlign: 'right'}} />
      {/* {show && <Paper variant="outlined" sx={{position: 'absolute', zIndex: 10, left: 500, width: 500, p: 2, cursor: 'text'}}><Typography><b>Quote:</b> {raceStats.race.quote.quote}</Typography></Paper>} */}
    </ListItem>
    
  )
}

export default ListItemWithHover