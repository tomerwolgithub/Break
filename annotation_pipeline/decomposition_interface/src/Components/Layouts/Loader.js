import React from "react";
import PropTypes from "prop-types";
import { withStyles } from "@material-ui/core/styles";
import Typography from "@material-ui/core/Typography";
import NoSsr from "@material-ui/core/NoSsr";
import TextField from "@material-ui/core/TextField";
import AppBar from "@material-ui/core/AppBar";
import Toolbar from "@material-ui/core/Toolbar";
import IconButton from "@material-ui/core/IconButton";
import QuestionAnswerIcon from "@material-ui/icons/QuestionAnswer";
import CircularProgress from "@material-ui/core/CircularProgress";

const style = {
  AppBar: { padding: 5, marginTop: 10, marginBottom: 10 }
};

const styles = theme => ({
  root: {
    flexGrow: 1
  },
  input: {
    display: "flex",
    padding: 0
  },
  placeholder: {
    position: "absolute",
    left: 2,
    fontSize: 16
  },
  paper: {
    position: "absolute",
    zIndex: 1,
    marginTop: theme.spacing.unit,
    left: 0,
    right: 0
  },
  divider: {
    height: theme.spacing.unit * 2
  }
});

function inputComponent({ inputRef, ...props }) {
  return <div ref={inputRef} {...props} />;
}

function Placeholder(props) {
  return (
    <Typography
      color="textSecondary"
      className={props.selectProps.classes.placeholder}
      {...props.innerProps}
    >
      {props.children}
    </Typography>
  );
}

const components = {
  Placeholder,
};

class IntegrationReactSelect extends React.Component {
  constructor() {
    super();

    this.state = {
      input: null,
      questions: null,
      isLoading: false,
      error: null,
      testing: null,
      invalid_question_id: false
    };
  }

  handleChange(e) {
    ///console.log("input is:", e.target.value);
    this.setState({ input: e.target.value.trim() });
  }

  keyPress(e) {
    // user pressed enter
    if (e.keyCode === 13) {
      // question id format: SPIDER_train_3983
      let re = /^(\s*)+[A-Z2]+_[a-z]+_[A-Za-z0-9\-\_]+(\s*)+$/;
      let re2 = /^(\s*)+[A-Z]+_[a-z]+_[a-z]+_[0-9]+_[A-Za-z0-9\-]+(\s*)+$/;
      let re_granular = /^(\s*)+[LOW]+_[A-Z]+_[a-z]+_[a-z]+_[0-9]+_[A-Za-z0-9\-]+(\s*)+$/;
      let re_granular2 = /^(\s*)+[LOW]+_[A-Z]+_[a-z]+_[A-Za-z0-9\-\_]+(\s*)+$/;
      let question_id = this.state.input;
      // deal with granular question ids (start with 'LOW_')
      let granularInputID_DROP = re_granular.test(question_id);
      let granularInputID = re_granular2.test(question_id);
      if (granularInputID_DROP || granularInputID){
        // prune the 'LOW_' prefix
        question_id = this.state.input.substring(4);
      }
      let validInput = re.test(question_id);
      if (!validInput){
        // try other question id format: DROP_dev_history_69_6ebee2d1-4f22
        validInput = re2.test(question_id);
      }
      if (validInput) {
        console.log("valid input is:", question_id);
        this.loadQuestion(question_id);
      } else {
        console.log("invalid input is:", question_id);
        this.setState({ invalid_question_id: true });
      }
    }
  }

  loadQuestion(q_id) {
    console.log("question object is:", this.state.questions[q_id])
    let question = this.state.questions[q_id]
    if (question === undefined){
      this.setState({ invalid_question_id: true });
    }else{
      this.setState({ invalid_question_id: false });
      this.props.onLoadQuestion(q_id, question)
    }
    return;
  }

  componentDidMount() {
    /// Fatching the questions data json
    this.setState({ isLoading: true }, () => {
      console.log("isLoading:", this.state.isLoading)});
    fetch("./store.json")
      .then(response => {
        if (response.ok) {
          return response.json();
        } else {
          throw new Error("Something went wrong ...");
        }
      })
      .then(data => this.setState({ questions: data, isLoading: false, testing: "is set now" }, () => {
        console.log("questions:", this.state.questions)
       console.log("isLoading:", this.state.isLoading);
      }))
      .catch(error => this.setState({ error, isLoading: false }));
  }

  render() {
    // Start by loading the questions data
    const isLoading = this.state.isLoading;
    const error = this.state.error;
    const invalid_question_id = this.state.invalid_question_id;

    if (error) {
      return (
        <p>{"Error: " + error.message}</p>
        );
    }

    if (isLoading) {
      return (
        <div>
          <p>Loading ...</p>
          <CircularProgress />
        </div>
      );
    }

    const { classes } = this.props;

    return (
      <div className={classes.root} style={{ display: "inline-block" }}>
        <NoSsr>
          <AppBar position="static" color="action" style={style.AppBar}>
            <Toolbar>
              <IconButton
                color="inherit"
                aria-label="Open drawer"
              >
                <QuestionAnswerIcon />
              </IconButton>
              <div className={classes.grow} />
              <div className={classes.search}>
                <TextField
                  classes={classes}
                  style={{ width: 700 }}
                  label={invalid_question_id ? "Invalid question id" : "Load question, then press ''Enter''"}
                  components={components}
                  value={this.state.single}
                  onChange={this.handleChange.bind(this)}
                  onKeyDown={this.keyPress.bind(this)}
                  placeholder="Insert question id..."
                  isClearable
                />
              </div>
            </Toolbar>
          </AppBar>
        </NoSsr>
      </div>
    );
  }
}

IntegrationReactSelect.propTypes = {
  classes: PropTypes.object.isRequired,
  theme: PropTypes.object.isRequired
};

export default withStyles(styles, { withTheme: true })(IntegrationReactSelect);
