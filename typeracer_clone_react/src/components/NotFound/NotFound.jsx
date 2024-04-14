import { Avatar, Box, Button, Container, CssBaseline, Grid, Paper, TextField, Typography } from '@mui/material'
import { Home } from '@mui/icons-material'
import React from 'react'
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline';
import { Link } from 'react-router-dom';

const PageNotFound = () => {
  return(
    <Container component="main" maxWidth="sm">
        <CssBaseline />

        <Grid
        container
        spacing={0}
        direction="column"
        alignItems="center"
        justifyContent="center"
        sx={{ minHeight: '100vh' }}
        >
        <Grid item xs={3}>
        <Box
          sx={{
            // marginTop: 8,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
          }}
        >
          <Typography component="h1" variant="h1">
            404
          </Typography>
          <Typography component="h1" variant="h4">
            Ooops!
          </Typography>
          <Typography component="h1" variant="h5">
            THIS PAGE DOESN'T EXIST OR IS UNAVAILABLE.
          </Typography>
          <Link to='/'><Button variant="contained">Return Home</Button></Link>
          
        </Box>
            
        </Grid>
        </Grid>


    </Container>
  )
}

export default PageNotFound
