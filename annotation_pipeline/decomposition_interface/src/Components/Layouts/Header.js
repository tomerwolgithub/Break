import React from "react";
import { withStyles } from "@material-ui/core/styles";
import AppBar from "@material-ui/core/AppBar";
import Toolbar from "@material-ui/core/Toolbar";
import Typography from "@material-ui/core/Typography";
import Button from "@material-ui/core/Button";
import IconButton from "@material-ui/core/IconButton";
import MenuIcon from "@material-ui/icons/Menu";

export default props => (
  <AppBar position="static" color="primary">
    <Toolbar>
      <Typography variant="headline" color="inherit">
        TDT - TAU Decomposition Task [original]
      </Typography>
    </Toolbar>
  </AppBar>
);
