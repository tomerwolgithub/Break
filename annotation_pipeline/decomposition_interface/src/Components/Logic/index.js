import React from "react";
import Grid from "@material-ui/core/Grid";
import Rightpane from "./RightPane";
import LeftPane from "./LeftPane";

const style = {
  Paper: { padding: 20, marginTop: 10, marginBottom: 10 }
};

export default ({
  items,
  onSelect,
  decomposition,
  decomposition_strings,
  annotation,
  steps,
  onAddStep,
  onEditStep,
  onDeleteStep,
  onDisplayDecomposition,
  question_id,
  question_text,
  valid_tokens,
  valid_preview
}) => (
  <Grid container>
    <Grid item xl>
      <LeftPane
        decomposition={decomposition}
        style={style}
        steps={steps}
        onAddStep={onAddStep}
        onEditStep={onEditStep}
        onDeleteStep={onDeleteStep}
        onDisplayDecomposition={onDisplayDecomposition}
        question_id={question_id}
        question_text={question_text}
        valid_tokens={valid_tokens}
      />
    </Grid>
    <Grid item xl>
      <Rightpane
        style={style}
        decomposition_strings={decomposition_strings}
        annotation={annotation}
        question_text={question_text}
        valid_preview={valid_preview}
      />
    </Grid>
  </Grid>
);
