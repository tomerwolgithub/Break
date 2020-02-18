import React, { Fragment, Component } from "react";
import Header from "./Layouts/Header";
import Carousel from "./Layouts/Carousel";
import Logic from "./Logic";
import Loader from "./Layouts/Loader";

export default class extends Component {
  state = {
    question_id: null,
    question_text: null,
    valid_tokens: null,
    decomposition: [{ id: 1, value: null }],
    steps_num: 1,
    decomposition_strings: [""],
    annotation: [],
    valid_preview: false
  };

  handleLoadQuestion = (id, question) => {
    if (question === null) {
      return;
    }
    this.setState(({ question_id, question_text, valid_tokens }) => ({
      question_id: id,
      question_text: question.text,
      valid_tokens: question.valid_tokens
    }));
  };

  handleEditStep = step =>
    this.setState(({ decomposition }) => ({
      decomposition: [
        ...this.state.decomposition.slice(0, step.id - 1),
        step,
        ...this.state.decomposition.slice(
          step.id,
          this.state.decomposition.length
        )
      ],
      valid_preview: false
    }));

  handleAddStep = step =>
    this.setState(({ decomposition }) => ({
      decomposition: [...decomposition, step],
      steps_num: this.state.steps_num + 1,
      valid_preview: false
    }));

  handleDeleteStep = id => {
    console.log("Before handleDeleteStep this.state.decomposition");
    console.log(this.state.decomposition);
    this.deleteStep(id);
    console.log("After handleDeleteStep this.state.decomposition");
    console.log(this.state.decomposition);
  };

  updateStepIds(id) {
    var newDecomposition = [];
    var decompLength = this.state.decomposition.filter(stp => stp.id !== id)
      .length;
    for (var i = 0; i < decompLength; i++) {
      var newId = this.state.decomposition.filter(stp => stp.id !== id)[i].id;
      var newValue = this.state.decomposition.filter(stp => stp.id !== id)[i].value;
      if (newId > id) {
        newId = newId - 1;
      }
      newDecomposition[i] = { id: newId, value: newValue };
    }
    this.setState(({ decomposition }) => ({
      decomposition: newDecomposition,
      steps_num: this.state.steps_num - 1
    }));
  }

  deleteStep(id) {
    if (this.state.decomposition.length > 1) {
      this.updateStepIds(id);
      this.changePreviewState(false);
    }
  }

  setDecompositionString(id) {
    let step_str = "";
    let decomposition_strings = this.state.decomposition_strings;
    var stepLength = 0;
    var step_words = this.state.decomposition[id - 1].value;
    var annotation_step = "";
    var annotation = this.state.annotation;
    // check if decomposition step is empty
    if (step_words == null) {
      return;
    }
    stepLength = step_words.length;
    for (var i = 0; i < stepLength; i++) {
      // set the snnotation step tokens
      annotation_step = annotation_step + step_words[i].label + " ";
      // deal with the display strings
      if (step_words[i].label.startsWith("#")) {
        // check if this is a previous step
        let prev_step_id = parseInt(step_words[i].label.substr(1));
        var prev_step = "<ERROR - invalid step reference!>";
        if (prev_step_id < id) {
          prev_step = decomposition_strings[prev_step_id - 1];
        }
        step_str = step_str + prev_step + " ";
      } else {
        step_str = step_str + step_words[i].label + " ";
      }
    }
    annotation[id - 1] = "return " + annotation_step;
    decomposition_strings[id - 1] = step_str;
    this.setState(({ decomposition_strings, annotation }) => ({
      decomposition_strings: decomposition_strings,
      annotation: annotation
    }));
  }

  handleDisplayDecomposition = () => {
    for (var id = 1; id < this.state.decomposition.length + 1; id++) {
      this.setDecompositionString(id);
    }
    // prune the decomposition string array if needed
    this.setState(({ decomposition_strings }) => ({
      decomposition_strings: this.state.decomposition_strings.slice(0, this.state.decomposition.length)
    }));
    // prune the annotation string array if needed
    this.setState(({ annotation }) => ({
      annotation: this.state.annotation.slice(0, this.state.decomposition.length)
    }));
    console.log("Before this.state.valid_preview");
    console.log(this.state.valid_preview);
    this.changePreviewState(true);
  };


  changePreviewState(is_valid) {
    this.setState({ valid_preview: is_valid }, function() {
      console.log("After this.state.valid_preview");
      console.log(this.state.valid_preview);
    });
    return this.state.valid_preview;
  }

  checkMap = () => {
    const listItems = this.state.decomposition.map(number => <li>{number}</li>);
    return listItems;
  };

  render() {
    return this.state.question_id === null ? (
      <Fragment>
        <Header />
        <Carousel />
        <Loader onLoadQuestion={this.handleLoadQuestion} />
      </Fragment>
    ) : (
      <Fragment>
        <Header />
        <Carousel />
        <Logic
          decomposition={this.state.decomposition}
          decomposition_strings={this.state.decomposition_strings}
          annotation={this.state.annotation}
          steps={this.state.steps_num}
          onAddStep={this.handleAddStep}
          onEditStep={this.handleEditStep}
          onDeleteStep={this.handleDeleteStep}
          onDisplayDecomposition={this.handleDisplayDecomposition}
          question_id={this.state.question_id}
          question_text={this.state.question_text}
          valid_tokens={this.state.valid_tokens}
          valid_preview={this.state.valid_preview}
        />
      </Fragment>
    );
  }
}
