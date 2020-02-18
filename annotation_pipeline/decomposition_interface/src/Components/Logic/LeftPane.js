import React from "react";
import Paper from "@material-ui/core/Paper";
import AppBar from "@material-ui/core/AppBar";
import Toolbar from "@material-ui/core/Toolbar";
import Typography from "@material-ui/core/Typography";
import Button from "@material-ui/core/Button";
import LoopIcon from "@material-ui/icons/Loop";
import Step from "./Step";
import Fab from "@material-ui/core/Fab";
import AddIcon from "@material-ui/icons/Add";

export default ({
  decomposition,
  style,
  steps,
  onAddStep,
  onEditStep,
  onDeleteStep,
  onDisplayDecomposition,
  question_id,
  question_text,
  valid_tokens
}) => (
  <Paper style={style.Paper}>
    <AppBar position="static" color="default">
      <Toolbar>
        <Typography variant="subtitle2" color="inherit" style={{ paddingTop: 0, paddingBottom: 0}}>
            {"[ Question id : " + question_id + " ]"}
        </Typography>
      </Toolbar>
      <Toolbar>
        <Typography variant="subtitle1" color="inherit" style={{ marginTop: 0, marginBottom: 0}}>
            {question_text }
        </Typography>
      </Toolbar>
    </AppBar>
    {decomposition.map(({ id, value }) =>
      id !== decomposition.length || id === 1 ? (
        <Step
          number={id}
          onEdit={onEditStep}
          onDelete={onDeleteStep}
          initialPhraseValue={value}
          decomposition={decomposition}
          deleteButton={false}
          valid_tokens={valid_tokens}
        />
      ) : (
        <Step
          number={id}
          onEdit={onEditStep}
          onDelete={onDeleteStep}
          initialPhraseValue={value}
          decomposition={decomposition}
          deleteButton={true}
          valid_tokens={valid_tokens}
        />
      )
    )}

    <Fab
      size="small"
      color="default"
      aria-label="Add"
      style={{ marginTop: 10, marginBottom: 20 }}
      onClick={() => onAddStep({ id: steps + 1, value: null })}
    >
      <AddIcon />
    </Fab>
    <div>
      <Button
        variant="contained"
        color="primary"
        onClick={() => onDisplayDecomposition()}
      >
        Display Results
        <LoopIcon />
      </Button>
    </div>
  </Paper>
);
