import * as React from 'react';
import PropTypes from 'prop-types';
import Backdrop from '@mui/material/Backdrop';
import Box from '@mui/material/Box';
import Modal from '@mui/material/Modal';
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';
import { useSpring, animated } from '@react-spring/web';
import { useNavigate } from "react-router-dom";

const Fade = React.forwardRef(function Fade(props, ref) {
  const {
    children,
    in: open,
    onClick,
    onEnter,
    onExited,
    ownerState,
    ...other
  } = props;
  const style = useSpring({
    from: { opacity: 0 },
    to: { opacity: open ? 1 : 0 },
    onStart: () => {
      if (open && onEnter) {
        onEnter(null, true);
      }
    },
    onRest: () => {
      if (!open && onExited) {
        onExited(null, true);
      }
    },
  });

  return (
    <animated.div ref={ref} style={style} {...other}>
      {React.cloneElement(children, { onClick })}
    </animated.div>
  );
});

Fade.propTypes = {
  children: PropTypes.element.isRequired,
  in: PropTypes.bool,
  onClick: PropTypes.any,
  onEnter: PropTypes.func,
  onExited: PropTypes.func,
  ownerState: PropTypes.any,
};

const style = {
  position: 'absolute',
  top: '50%',
  left: '50%',
  transform: 'translate(-50%, -50%)',
  width: 400,
  bgcolor: 'background.paper',
  //border: '2px solid #000',
  boxShadow: 24,
  p: 4,
};

export default function SpringModal({modalOpen, handleModalClose, markAsLoggedOut}) {

  const navigate = useNavigate();

  const navigateToSignIn = () => {
    navigate("/signin");
  }

  const logOut = () => {
    fetch('/api/logout/', {
      method: 'POST',
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({refresh: localStorage.getItem('jwt-refresh')})
    })
    .then(response => {
      if(response.ok) { 
        markAsLoggedOut()
        handleModalClose()
        navigateToSignIn()
        localStorage.clear()
        sessionStorage.clear()
      } else {
        throw new Error(`Something went wrong, server response status code is ${response.status}`);
      }
    })
    .catch(err => {
      console.error(err)
    })
  }

  return (
<div>
      <Modal
        aria-labelledby="spring-modal-title"
        aria-describedby="spring-modal-description"
        open={modalOpen}
        onClose={handleModalClose}
        closeAfterTransition
        slots={{ backdrop: Backdrop }}
        slotProps={{
          backdrop: {
            TransitionComponent: Fade,
          },
        }}
      >
        <Fade in={modalOpen}>
          <Box sx={style}>
            <Typography id="spring-modal-title" variant="h6" component="h2" sx={{textAlign: 'center'}}>
              Are you sure you want to log out?
            </Typography>
            <Box sx={{display: 'flex', justifyContent: 'center'}}>
              <Button
                variant="outlined"
                // variant="contained"
                color="secondary"
                sx={{ mt: 3, mb: 2 , mr: 1}}
                onClick={logOut}
              >
                Logout
              </Button>  
              <Button
                variant="outlined"
                // variant="contained"
                sx={{ mt: 3, mb: 2 }}
                onClick={handleModalClose}
              >
                Cancel
              </Button> 
            </Box>
          </Box>
        </Fade>
      </Modal>
      </div>
  );
}