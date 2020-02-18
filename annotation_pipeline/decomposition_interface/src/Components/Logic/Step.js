import React from "react";
import PropTypes from "prop-types";
import { withStyles } from "@material-ui/core/styles";
import TextField from "@material-ui/core/TextField";
import Divider from "@material-ui/core/Divider";
import DeleteIcon from "@material-ui/icons/Delete";
import Button from "@material-ui/core/Button";
import Phrase from "./Phrase";

const styles = theme => ({
  margin: {
    margin: theme.spacing.unit
  }
});

function InputWithIcon(props) {
  const { classes } = props;

  return (
    <div>
      <form>
        <TextField
          id="standard-read-only-input"
          label="Step"
          defaultValue={"#" + props.number}
          className={classes.textField}
          margin="normal"
          InputProps={{
            readOnly: true
          }}
          style={{ width: 40 }}
        />

        <TextField
          id="standard-read-only-input"
          label="return"
          defaultValue="Return"
          className={classes.textField}
          margin="normal"
          InputProps={{
            readOnly: true
          }}
          style={{ width: 70 }}
        />

        <Phrase
          onEdit={props.onEdit}
          num={props.number}
          items={props.items}
          initialValue={props.initialPhraseValue}
          decomposition={props.decomposition}
          valid_tokens={props.valid_tokens}
        />
        <div>
          {props.deleteButton ? (
            <Button title="Delete last step">
              <DeleteIcon onClick={() => props.onDelete(props.number)} />
            </Button>
          ) : (
            <div />
          )}
        </div>
      </form>

      <Divider style={{ height: 6 }} />
    </div>
  );
}

InputWithIcon.propTypes = {
  classes: PropTypes.object.isRequired
};

export default withStyles(styles)(InputWithIcon);
