import React from "react";
import Button from "@material-ui/core/Button";
import Dialog from "@material-ui/core/Dialog";
import DialogActions from "@material-ui/core/DialogActions";
import DialogContent from "@material-ui/core/DialogContent";
import DialogContentText from "@material-ui/core/DialogContentText";
import DialogTitle from "@material-ui/core/DialogTitle";
import CheckIcon from "@material-ui/icons/Check";

class AlertDialog extends React.Component {
  state = {
    open: false,
    copySuccess: ""
  };

  copyToClipboard = e => {
    this.textArea.select();
    document.execCommand("copy");
    // This is just personal preference.
    // I prefer to not show the the whole text area selected.
    e.target.focus();
    this.setState({ copySuccess: "Code copied to clipboard!" });
  };

  handleClickOpen = () => {
    this.setState({ open: true });
  };

  handleClose = () => {
    this.setState({ open: false, copySuccess: "" });
  };

  render() {
    return (
      <div>
        <Button
          variant="contained"
          color="primary"
          onClick={this.handleClickOpen}
          disabled={!this.props.valid_preview}
        >
          Submit
          {console.log("Dialog this.props.annotation.valid_preview")}
          {console.log(this.props.valid_preview)}
          <CheckIcon />
        </Button>
        <Dialog
          open={this.state.open}
          onClose={this.handleClose}
          aria-labelledby="alert-dialog-title"
          aria-describedby="alert-dialog-description"
        >
          <DialogTitle id="alert-dialog-title">{"HIT Submission"}</DialogTitle>
          <DialogContent>
            <DialogContentText id="alert-dialog-description">
              Thank you for completing this HIT. Your generated decomposition
              will serve as the survey code to be submitted to the Amazon
              Mechanical Turk website.
              <p>
                You should copy the code from the textbox below and paste in the
                Amazon Mechanical Turk interface as your survey code.
              </p>
              <p>
                <b>
                  Without submitting a valid code your HIT will be automatically
                  rejected!
                </b>
              </p>
            </DialogContentText>
            <div>
              {/* Logical shortcut for only displaying the 
            button if the copy command exists */
              document.queryCommandSupported("copy") && (
                <div>
                  <Button
                    variant="outlined"
                    color="primary"
                    onClick={this.copyToClipboard}
                  >
                    Copy
                  </Button>
                  {this.state.copySuccess}
                </div>
              )}
              <form>
                <textarea
                  ref={textarea => (this.textArea = textarea)}
                  value={this.props.annotation.join(";").toString()}
                />
              </form>
            </div>
          </DialogContent>
          <DialogActions>
            <Button onClick={this.handleClose} color="primary">
              Close
            </Button>
          </DialogActions>
        </Dialog>
      </div>
    );
  }
}

export default AlertDialog;
