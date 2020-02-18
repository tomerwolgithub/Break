import React, { Fragment } from "react";
import PropTypes from "prop-types";
import { withStyles } from "@material-ui/core/styles";
import MobileStepper from "@material-ui/core/MobileStepper";
import Typography from "@material-ui/core/Typography";
import Button from "@material-ui/core/Button";
import KeyboardArrowLeft from "@material-ui/icons/KeyboardArrowLeft";
import KeyboardArrowRight from "@material-ui/icons/KeyboardArrowRight";
import Card from "@material-ui/core/Card";
import CardContent from "@material-ui/core/CardContent";
import Badge from "@material-ui/core/Badge";
import List from "@material-ui/core/List";
import ListSubheader from "@material-ui/core/ListSubheader";
import ListItem from "@material-ui/core/ListItem";
import ListItemText from "@material-ui/core/ListItemText";
import ListItemIcon from "@material-ui/core/ListItemIcon";
import WarningIcon from "@material-ui/icons/Warning";
import ExpansionPanel from "@material-ui/core/ExpansionPanel";
import ExpansionPanelSummary from "@material-ui/core/ExpansionPanelSummary";
import ExpansionPanelDetails from "@material-ui/core/ExpansionPanelDetails";
import ExpandMoreIcon from "@material-ui/icons/ExpandMore";
import Divider from "@material-ui/core/Divider";
import red from "@material-ui/core/colors/red";

const color_err = red[900];

const style = {
  Card: { padding: 5, marginTop: 10, marginBottom: 10, width: 800 },
  Stepper: { padding: 5, marginTop: 10, marginBottom: 10 },
  Typography: { flexBasis: "20%", flexShrink: 0, fontWeight: "bold" }
};

const myFlex = "35%";

const styles = theme => ({
  root: {
    maxWidth: 600,
    flexGrow: 1
  },
  header: {
    display: "flex",
    alignItems: "center",
    height: 50,
    paddingLeft: theme.spacing.unit * 4,
    backgroundColor: theme.palette.background.default
  },
  img: {
    height: 255,
    maxWidth: 600,
    overflow: "hidden",
    display: "block",
    width: "100%"
  }
});

const tutorialSteps = [
  {
    title: "Instructions",
    label: (
      <div>
        <p>
          Welcome to the TAU decomposition task. In this task you will break
          down a question into the basic steps required in order to answer it.
          Imagine explaining your question to a friendly droid by listing each
          action it should take in order for the question to be answered.
        </p>
        <p>
          <b>
            <font color="magenta">
              The guidelines for correct decompositions have been changed once
              more!
              <br />
              We are now trageting decompositions of yes/no questions over
              images.
              <br />
              These decompositions are more granular in nature. A list of
              image-specific examples has been added.
              <br />
            </font>
            <font color="red">
              Please review the new image decomposition examples next.
            </font>
          </b>
        </p>
        <p>
          This HIT is comprised of several stages:
          <ol>
            <li>
              Insert the question id listed in your MTurk HIT in order to load
              your question.
            </li>
            <li>
              Go over the decomposition instructions and the examples we have
              supplied you with.
            </li>
            <li>
              Use the interface in order to write, add and delete decompostion
              steps for the question.
            </li>
            <li>
              Display your decomposition results and review their correctness.
            </li>
            <li>
              Once you have displayed your decomposition press the 'Submit'
              button.
            </li>
            <li>
              In the submit window, copy your survey code and paste it to the
              MTurk website.
            </li>
          </ol>
        </p>
        <p>
          <b>Important:</b> all your results will be reviewed and judged for
          their quality. We urge you to take your time in reviewing and
          understanding the decomposition examples we provide. Workers that will
          continuously submit decompositions of poor quality will be prohibited
          from submitting future TDT HITs.
        </p>
        <font color="red">
          <p>
            <b>
              Click 'Next' to review the new image question decomposition
              examples.
            </b>
          </p>
        </font>
      </div>
    )
  },
  {
    title: "*NEW* Yes/No Image Decompositions",
    label: (
      <div>
        <p>
          This task is similar to our original question decomposition task.
          <br />
          You are presented with decomposing a yes/no question posed on an
          unseen image. For example:
          <ul>
            <li>
              "If exactly one image shows a suite of devices on a plain
              background."
            </li>
          </ul>
          Its correct decomposition should be:
          <ol>
            <li>Return suite of devices</li>
            <li>Return plain background</li>
            <li>Return #1 on #2</li>
            <li>Return if #3 is in exactly one image</li>
          </ol>
          Note that there are several changes from our classic decompositions:
          <br />
          The yes/no question must end with an "is true" ("if") step. This step
          is a full statement regarding the condition posed in the orginal
          question, ("... is in exactly one image").
          <br />
          Steps #1 and #2 each return an object or entity present in the unseen
          image.
          <br />
          Step #3 then explicitly <b>states the relation</b> between the two
          objects ("#1 on #2").
        </p>
        <p>
          Listed below are several examples of image questions and their correct
          decompositions.
          <br />
          <font color="red">
            <b>
              Make sure to review the examples before submitting any new HITs!
            </b>
          </font>
        </p>
        <p>
          <hr />
          <List component="nav">
            <ListItem button>
              <ListItemText
                primary={
                  "(A)  If the animals are running with their front legs air bound."
                }
              />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#1</ListItemIcon>
              <ListItemText disableTypography primary={"Return animals"} />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#2</ListItemIcon>
              <ListItemText
                disableTypography
                primary={"Return #1 that are running"}
              />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#3</ListItemIcon>
              <ListItemText
                disableTypography
                primary={"Return front legs of #2"}
              />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#4</ListItemIcon>
              <ListItemText
                disableTypography
                primary={"Return if #3 are air bound"}
              />
            </ListItem>
          </List>
          <hr />
          <List component="nav">
            <ListItem button>
              <ListItemText
                primary={
                  "(B)  If an image shows a woman bending forward while holding dumbell weights."
                }
              />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#1</ListItemIcon>
              <ListItemText disableTypography primary={"Return woman"} />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#2</ListItemIcon>
              <ListItemText
                disableTypography
                primary={"Return #1 bending forward"}
              />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#3</ListItemIcon>
              <ListItemText
                disableTypography
                primary={"Return dumbell weights"}
              />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#4</ListItemIcon>
              <ListItemText
                disableTypography
                primary={"Return #2 holding #3"}
              />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#5</ListItemIcon>
              <ListItemText
                disableTypography
                primary={"Return if #4 is in an image"}
              />
            </ListItem>
          </List>
          <hr />
          <List component="nav">
            <ListItem button>
              <ListItemText
                primary={
                  "(C)  If one image contains exactly two roller skates and two pads."
                }
              />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#1</ListItemIcon>
              <ListItemText
                disableTypography
                primary={"Return roller skates"}
              />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#2</ListItemIcon>
              <ListItemText disableTypography primary={"Return pads"} />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#3</ListItemIcon>
              <ListItemText disableTypography primary={"Return number of #1"} />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#4</ListItemIcon>
              <ListItemText disableTypography primary={"Return number of #2"} />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#5</ListItemIcon>
              <ListItemText
                disableTypography
                primary={"Return if #3 is equal to two"}
              />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#6</ListItemIcon>
              <ListItemText
                disableTypography
                primary={"Return if #4 is equal to two"}
              />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#7</ListItemIcon>
              <ListItemText
                disableTypography
                primary={"Return if both #5 and #6 are true"}
              />
            </ListItem>
          </List>
          <hr />
          <List component="nav">
            <ListItem button>
              <ListItemText
                primary={
                  "(D)  If each image contains at least three baked stuffed potatos."
                }
              />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#1</ListItemIcon>
              <ListItemText
                disableTypography
                primary={"Return baked stuffed potatos"}
              />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#2</ListItemIcon>
              <ListItemText disableTypography primary={"Return images of #1"} />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#3</ListItemIcon>
              <ListItemText
                disableTypography
                primary={"Return number of #1 for each #2"}
              />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#4</ListItemIcon>
              <ListItemText
                disableTypography
                primary={"Return #2 where #3 is at least three"}
              />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#5</ListItemIcon>
              <ListItemText disableTypography primary={"Return number of #4"} />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#6</ListItemIcon>
              <ListItemText disableTypography primary={"Return number of #2"} />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#7</ListItemIcon>
              <ListItemText
                disableTypography
                primary={"Return if #5 is equal to #6"}
              />
            </ListItem>
          </List>
          <hr />
          <List component="nav">
            <ListItem button>
              <ListItemText
                primary={
                  "(E)  If one image includes a forward-facing standing llama, and the other image includes a reclining llama with another llama alongside it."
                }
              />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#1</ListItemIcon>
              <ListItemText disableTypography primary={"Return one image"} />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#2</ListItemIcon>
              <ListItemText disableTypography primary={"Return llama of #1"} />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#3</ListItemIcon>
              <ListItemText
                disableTypography
                primary={"Return #2 that is forward facing"}
              />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#4</ListItemIcon>
              <ListItemText
                disableTypography
                primary={"Return if #3 is standing"}
              />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#5</ListItemIcon>
              <ListItemText disableTypography primary={"Return other image"} />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#6</ListItemIcon>
              <ListItemText disableTypography primary={"Return llama of #5"} />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#7</ListItemIcon>
              <ListItemText
                disableTypography
                primary={"Return #6 that is reclining"}
              />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#8</ListItemIcon>
              <ListItemText
                disableTypography
                primary={"Return if #7 is alongside #6"}
              />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#9</ListItemIcon>
              <ListItemText
                disableTypography
                primary={"Return if both #4 and #8 are true"}
              />
            </ListItem>
          </List>
          <hr />
          <List component="nav">
            <ListItem button>
              <ListItemText
                primary={
                  "(F)  If there are more pelican birds in the right image than in the left."
                }
              />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#1</ListItemIcon>
              <ListItemText disableTypography primary={"Return right image "} />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#2</ListItemIcon>
              <ListItemText disableTypography primary={"Return left image"} />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#3</ListItemIcon>
              <ListItemText
                disableTypography
                primary={"Return pelican birds in #1"}
              />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#4</ListItemIcon>
              <ListItemText
                disableTypography
                primary={"Return pelican birds in #2"}
              />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#5</ListItemIcon>
              <ListItemText disableTypography primary={"Return number of #3"} />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#6</ListItemIcon>
              <ListItemText disableTypography primary={"Return number of #4"} />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#7</ListItemIcon>
              <ListItemText
                disableTypography
                primary={"Return if #5 is higher than #6"}
              />
            </ListItem>
          </List>
          <hr />
          <List component="nav">
            <ListItem button>
              <ListItemText
                primary={
                  "(G)  If an image with no more than three gorillas shows an adult sitting behind a small juvenile ape."
                }
              />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#1</ListItemIcon>
              <ListItemText disableTypography primary={"Return gorilla"} />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#2</ListItemIcon>
              <ListItemText
                disableTypography
                primary={"Return #1 that is adult"}
              />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#3</ListItemIcon>
              <ListItemText
                disableTypography
                primary={"Return #1 that is juvenile"}
              />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#4</ListItemIcon>
              <ListItemText
                disableTypography
                primary={"Return #3 that is small"}
              />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#5</ListItemIcon>
              <ListItemText
                disableTypography
                primary={"Return if #2 is sitting behind #4"}
              />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#6</ListItemIcon>
              <ListItemText disableTypography primary={"Return number of #1"} />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#7</ListItemIcon>
              <ListItemText
                disableTypography
                primary={"Return if #6 is at most three"}
              />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#7</ListItemIcon>
              <ListItemText
                disableTypography
                primary={"Return if both #5 and #7 are true"}
              />
            </ListItem>
          </List>
          <hr />
          <List component="nav">
            <ListItem button>
              <ListItemText
                primary={
                  "(H)  If in at most one image, there's a parrot perched on a branch."
                }
              />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#1</ListItemIcon>
              <ListItemText disableTypography primary={"Return parrot"} />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#2</ListItemIcon>
              <ListItemText disableTypography primary={"Return branch"} />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#3</ListItemIcon>
              <ListItemText
                disableTypography
                primary={"Return #1 perched on #2"}
              />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#4</ListItemIcon>
              <ListItemText
                disableTypography
                primary={"Return if #3 is in at most one image"}
              />
            </ListItem>
          </List>
        </p>

        <p>
          <b>Click 'Next' read how to write a question decomposition.</b>
        </p>
      </div>
    )
  },
  {
    title: "How to write a question decomposition",
    label: (
      <div>
        <p>
          Imagine you are given a question such as:
          <ul>
            <li>
              "How many yards longer was Phil Dawson's longest field goal than
              his shortest?"
            </li>
          </ul>
          Now how would you solve such a question? What actions or "steps" need
          to be taken in order to provide the response?
          <br />A <b>question decomposition</b> is a numbered list of operations
          that must be performed to answer the original question.
          <br />
          Let's go back to our example question, we need to return the
          difference in yards between Phil Dawson's longest and shortest field
          goals. Thus, to solve the question we need to:
          <ol>
            <li>Return Phil Dawson</li>
            <li>Return the yards of his field goals</li>
            <li>Return the longest of the yards</li>
            <li>Return the shortest of the yards</li>
            <li>Return the their difference</li>
          </ol>
          Note that this is actually a numbered list of actions that refer to
          results of previous steps. Hence we can (and will) use{" "}
          <b>references to previous steps</b>:
          <ol>
            <li>Return Phil Dawson</li>
            <li>
              Return field goals of <b>#1</b>
            </li>
            <li>
              Return yards of <b>#2</b>
            </li>
            <li>
              Return the longest of <b>#3</b>
            </li>
            <li>
              Return the shortest of <b>#4</b>
            </li>
            <li>
              Return the difference of <b>#4</b> and <b>#5</b>
            </li>
          </ol>
        </p>
        Each step in our decomposition should refer to either an <b>entity</b>{" "}
        (known or unknown), a <b>propery</b> of an entity or a{" "}
        <b>query operation</b> (count, group, union, etc.).
        <br />
        In the example below step #1 returns the <b>entity</b> Phil Dawson,
        while steps #2-#3 return <b>properties</b> of Phil Dawn and his field
        goals respectively. Step #4-#6 return query operations on previous
        results (max, min and difference).
        <p>
          <b>Click 'Next' to review the standard decomposition templates.</b>
        </p>
      </div>
    )
  },
  {
    title: "How to write steps",
    label: (
      <Fragment>
        <p>
          The question decomposition is a numbered list of actions that need to
          be taken in order to answer the original question. Each step should
          correspond to a single operation from the list below. When writing a
          decomposition step you should adhere to the templates listed in the
          table. Your evaluation will be judged based on your ability to produce
          correct decompositions with well templated steps.
        </p>
        <p>
          <b>Vocabulary: </b> when filling out a step you are restricted in the
          words that you may use. You vocabulary will consist of all words
          appearing in the original questions in addition to relevant stop words
          and operations (more than, at least, where, of, is, etc.).
        </p>
        <p>
          <b>
            Click 'Next' to review common pitfalls along with decomposition
            examples
          </b>
        </p>
        <div>
          <ExpansionPanel>
            <ExpansionPanelSummary>
              <Typography
                style={{
                  flexBasis: "20%",
                  flexShrink: 0,
                  fontWeight: "bold",
                  textDecorationLine: "underline"
                }}
              >
                Operation
              </Typography>
              <Typography
                style={{
                  flexBasis: myFlex,
                  fontWeight: "bold",
                  textDecorationLine: "underline"
                }}
              >
                Template
              </Typography>
              <Typography
                style={{
                  fontWeight: "bold",
                  textDecorationLine: "underline"
                }}
              >
                Example
              </Typography>
            </ExpansionPanelSummary>
          </ExpansionPanel>
          <ExpansionPanel>
            <ExpansionPanelSummary expandIcon={<ExpandMoreIcon />}>
              <Typography style={style.Typography}>SELECT</Typography>
              <Typography style={{ flexBasis: myFlex }}>
                Return [attributes]
              </Typography>
              <Typography>Return [flights]</Typography>
            </ExpansionPanelSummary>
            <ExpansionPanelDetails>
              <Typography>
                A select step is used to return a set of objects. There are no
                references to previous steps in a select step. Examples of
                select steps:
                <li>Return representatives</li>
                <li>Return movies</li>
                <li>Return faculty members</li>
                <li>Return Charles V</li>
              </Typography>
            </ExpansionPanelDetails>
          </ExpansionPanel>
          <ExpansionPanel>
            <ExpansionPanelSummary expandIcon={<ExpandMoreIcon />}>
              <Typography style={style.Typography}>FILTER</Typography>
              <Typography style={{ flexBasis: myFlex }}>
                Return [#step] [condition]
              </Typography>
              <Typography>
                Return [#1] [that has the mascot of a duck]
              </Typography>
            </ExpansionPanelSummary>
            <ExpansionPanelDetails>
              <Typography>
                A filter step is used to return results from a previous step to
                which a certain condition applies. Examples of filter steps:
                <li>Return #1 to Milwaukee</li>
                <li>Return #1 in the University of Michigan</li>
                <li>Return #2 that are silver</li>
              </Typography>
            </ExpansionPanelDetails>
          </ExpansionPanel>
          <ExpansionPanel>
            <ExpansionPanelSummary expandIcon={<ExpandMoreIcon />}>
              <Typography style={style.Typography}>PROJECT</Typography>
              <Typography style={{ flexBasis: myFlex }}>
                Return [attributes] of [#step]
              </Typography>
              <Typography>Return [the titles] of [#1]</Typography>
            </ExpansionPanelSummary>
            <ExpansionPanelDetails>
              <Typography>
                A project step should return certain attributes of the results
                of a previous step. Examples of project steps:
                <li>Return the first name of #1</li>
                <li>Return the id of #3</li>
                <li>Return the color of #2</li>
                <li>Return the distinct official languages of #2</li>
              </Typography>
            </ExpansionPanelDetails>
          </ExpansionPanel>
          <ExpansionPanel>
            <ExpansionPanelSummary expandIcon={<ExpandMoreIcon />}>
              <Typography style={style.Typography}>AGGREGATE</Typography>
              <Typography style={{ flexBasis: myFlex }}>
                Return the [aggregator] of [#step]
              </Typography>
              <Typography>Return the [average] of [#2]</Typography>
            </ExpansionPanelSummary>
            <ExpansionPanelDetails>
              <Typography>
                Examples of aggregation steps:
                <li>Return the number of #1</li>
                <li>Return the sum of #3</li>
                <li>Return the average of #2</li>
                <li>Return the highest of #1</li>
                <li>Return the lowest of #1</li>
                <li>Return the maximum of #1</li>
                <li>Return the minimum of #4</li>
              </Typography>
            </ExpansionPanelDetails>
          </ExpansionPanel>
          <ExpansionPanel>
            <ExpansionPanelSummary expandIcon={<ExpandMoreIcon />}>
              <Typography style={style.Typography}>GROUP</Typography>
              <Typography style={{ flexBasis: myFlex }}>
                Return the [aggregator] of [#step] for each [attribute]
              </Typography>
              <Typography>
                Return the [number] of [#3] for each [author]
              </Typography>
            </ExpansionPanelSummary>
            <ExpansionPanelDetails>
              <Typography>
                Examples of group steps:
                <li>Return the number of #1 for each club</li>
                <li>Return the sum of #3 for each country</li>
                <li>Return the average of #2 for each age group</li>
              </Typography>
            </ExpansionPanelDetails>
          </ExpansionPanel>
          <ExpansionPanel>
            <ExpansionPanelSummary expandIcon={<ExpandMoreIcon />}>
              <Typography style={style.Typography}>SUPERLATIVE</Typography>
              <Typography style={{ flexBasis: myFlex }}>
                Return [#step1] [where] [#step2] [is] [highest / lowest]
              </Typography>
              <Typography>Return [#2] [where] [#5] [is highest]</Typography>
            </ExpansionPanelSummary>
            <ExpansionPanelDetails>
              <Typography>
                Examples of superlative steps:
                <li>Return #3 where #1 is highest</li>
                <li>Return #2 where #4 is lowest</li>
              </Typography>
            </ExpansionPanelDetails>
          </ExpansionPanel>
          <ExpansionPanel>
            <ExpansionPanelSummary expandIcon={<ExpandMoreIcon />}>
              <Typography style={style.Typography}>COMPARATIVE</Typography>
              <Typography style={{ flexBasis: myFlex }}>
                Return [#step1] [where] [#step2] [comparator] [number]
              </Typography>
              <Typography>
                Return [#4] [where] [#1] [is more than] [10]
              </Typography>
            </ExpansionPanelSummary>
            <ExpansionPanelDetails>
              <Typography>
                Examples of comparative steps:
                <li>Return #2 where #3 is at most 5000</li>
                <li>Return #2 where #1 is at least 60</li>
                <li>Return #5 were #1 is less than 10</li>
                <li>Return #1 where #2 is higher than 4</li>
              </Typography>
            </ExpansionPanelDetails>
          </ExpansionPanel>
          <ExpansionPanel>
            <ExpansionPanelSummary expandIcon={<ExpandMoreIcon />}>
              <Typography style={style.Typography}>UNION</Typography>
              <Typography style={{ flexBasis: myFlex }}>
                Return [#step1] [or / ,] [#step2]
              </Typography>
              <Typography>Return [#3] [or] [#4]</Typography>
            </ExpansionPanelSummary>
            <ExpansionPanelDetails>
              <Typography>
                Examples of union steps:
                <li>Return #2, #3</li>
                <li>Return #1 or #2</li>
              </Typography>
            </ExpansionPanelDetails>
          </ExpansionPanel>
          <ExpansionPanel>
            <ExpansionPanelSummary expandIcon={<ExpandMoreIcon />}>
              <Typography style={style.Typography}>INTERSECTION</Typography>
              <Typography style={{ flexBasis: myFlex }}>
                Return [attribute] of both [#step1] and [#step2]
              </Typography>
              <Typography>Return [directors] of both [#1] and [#2]</Typography>
            </ExpansionPanelSummary>
            <ExpansionPanelDetails>
              <Typography>
                Examples of intersection steps:
                <li>Return the parties of both #1 and #2</li>
                <li>Return films of both #1 and #3</li>
                <li>Return objects of both #2 and #3</li>
              </Typography>
            </ExpansionPanelDetails>
          </ExpansionPanel>
          <ExpansionPanel>
            <ExpansionPanelSummary expandIcon={<ExpandMoreIcon />}>
              <Typography style={style.Typography}>DISCARD</Typography>
              <Typography style={{ flexBasis: myFlex }}>
                Return [#step1] besides [#step2]
              </Typography>
              <Typography>Return [#2] besides [#4]</Typography>
            </ExpansionPanelSummary>
            <ExpansionPanelDetails>
              <Typography>
                Examples of "discard" decompostion:
                <li>1. Return actors;</li>
                <li>2. Return Brad Pitt;</li>
                <li>3. Return #1 besides #2</li>
              </Typography>
            </ExpansionPanelDetails>
          </ExpansionPanel>
          <ExpansionPanel>
            <ExpansionPanelSummary expandIcon={<ExpandMoreIcon />}>
              <Typography style={style.Typography}>SORT</Typography>
              <Typography style={{ flexBasis: myFlex }}>
                Return [#step1] [ordered / sorted by] [#step2]
              </Typography>
              <Typography>Return [#1] [sorted by] [#2]</Typography>
            </ExpansionPanelSummary>
            <ExpansionPanelDetails>
              <Typography>
                Example decomposition involving "sort":
                <li>1. Return apartments;</li>
                <li>2. Return monthly rental of #1;</li>
                <li>3. Return #1 sorted by #2 in descending order</li>
              </Typography>
            </ExpansionPanelDetails>
          </ExpansionPanel>
          <ExpansionPanel>
            <ExpansionPanelSummary expandIcon={<ExpandMoreIcon />}>
              <Typography style={style.Typography}>IS TRUE</Typography>
              <Typography style={{ flexBasis: myFlex }}>
                Return [is / if] [condition]
              </Typography>
              <Typography>Return [if] [#1 is the same as #2]</Typography>
            </ExpansionPanelSummary>
            <ExpansionPanelDetails>
              <Typography>
                Examples of is true steps:
                <li>Return is #1 more than #2</li>
                <li>Return is #1 metallic</li>
                <li>Return is any of #1 purple</li>
              </Typography>
            </ExpansionPanelDetails>
          </ExpansionPanel>
          <ExpansionPanel>
            <ExpansionPanelSummary expandIcon={<ExpandMoreIcon />}>
              <Typography style={style.Typography}>ARITHMETIC</Typography>
              <Typography style={{ flexBasis: myFlex }}>
                Return the [arithmetic op.] of [#step1] [and] [#step2]
              </Typography>
              <Typography>
                Return the [difference] of [#1] [and] [#2]
              </Typography>
            </ExpansionPanelSummary>
            <ExpansionPanelDetails>
              <Typography>
                Examples of arithmetic steps:
                <li>Return the sum of #2 and #3</li>
                <li>Return the multiplication of #1 and #2</li>
                <li>Return the division of #4 and #3</li>
              </Typography>
            </ExpansionPanelDetails>
          </ExpansionPanel>
        </div>
      </Fragment>
    )
  },
  {
    title: "Common pitfalls and mistakes",
    label: (
      <Fragment>
        <p>
          We review common mistakes of workers in writing the question
          decompositions.
        </p>
        <div>
          <List
            component="nav"
            subheader={
              <ListSubheader component="div">
                <b>Contents</b>
              </ListSubheader>
            }
          >
            <a href="#no_reference">
              <ListItem>
                <ListItemIcon>
                  <WarningIcon />
                </ListItemIcon>
                <ListItemText inset primary="Not referring to previous steps" />
              </ListItem>
            </a>
            <a href="#no_full_decomposition">
              <ListItem>
                <ListItemIcon>
                  <Badge color="secondary" badgeContent={"+1"} showZero>
                    <WarningIcon />
                  </Badge>
                </ListItemIcon>
                <ListItemText inset primary="Steps not fully decomposed" />
              </ListItem>
            </a>
            <a href="#wrong_order">
              <ListItem>
                <ListItemIcon>
                  <Badge color="secondary" badgeContent={"+2"} showZero>
                    <WarningIcon />
                  </Badge>
                </ListItemIcon>
                <ListItemText inset primary="Decomposition order is wrong" />
              </ListItem>
            </a>
            <a href="#using_and">
              <ListItem>
                <ListItemIcon>
                  <Badge color="secondary" badgeContent={"+2"} showZero>
                    <WarningIcon />
                  </Badge>
                </ListItemIcon>
                <ListItemText inset primary="Improper use of 'and' in steps" />
              </ListItem>
            </a>
          </List>
        </div>
        <div>
          <Divider />
          <Divider />
          <Typography variant="h6" component="h2" id="no_reference">
            Not referring to previous steps
          </Typography>
          <p>
            In the example below the worker has provided the steps nessecary to
            answer the question but did not refer to any of the previous steps.
            The correct decomposition is listed below.
          </p>
          <List component="nav">
            <ListItem button>
              <ListItemText
                primary={
                  "Show the name of all bridges that were designed by american architects, and sort the result by the bridge feet length."
                }
              />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#1</ListItemIcon>
              <ListItemText
                disableTypography
                style={{ color: color_err }}
                primary={"Return american architects"}
              />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#2</ListItemIcon>
              <ListItemText
                disableTypography
                style={{ color: color_err }}
                primary={"Return bridges"}
              />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#3</ListItemIcon>
              <ListItemText
                disableTypography
                style={{ color: color_err }}
                primary={"Return sorted by feet length"}
              />
            </ListItem>
          </List>
          <p>The correct decomposition being:</p>
          <List component="nav">
            <ListItem button>
              <ListItemIcon>#1</ListItemIcon>
              <ListItemText
                disableTypography
                primary={"Return american architects"}
              />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#2</ListItemIcon>
              <ListItemText
                disableTypography
                primary={"Return the bridges desgined by #1"}
              />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#3</ListItemIcon>
              <ListItemText
                disableTypography
                primary={"Return bridge feet length of #2"}
              />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#4</ListItemIcon>
              <ListItemText
                disableTypography
                primary={"Return #2 sorted by #3"}
              />
            </ListItem>
          </List>
        </div>
        <div>
          <Divider />
          <Divider />
          <Typography variant="h6" component="h2" id="no_full_decomposition">
            Steps not fully decomposed
          </Typography>
          <p>
            In this example the worker failed to decompose the question into{" "}
            <b>all</b> of its basic steps. The first step should be further
            decomposed as we must first return "american architects" before we
            can return the bridges designed by them.
          </p>
          <List component="nav">
            <ListItem button>
              <ListItemText
                primary={
                  "Show the name of all bridges that were designed by american architects, and sort the result by the bridge feet length."
                }
              />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#1</ListItemIcon>
              <ListItemText
                disableTypography
                style={{ color: color_err }}
                primary={"Return all bridges designed by american architects"}
              />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#2</ListItemIcon>
              <ListItemText
                disableTypography
                style={{ color: color_err }}
                primary={"Return #1 sorted by feet length"}
              />
            </ListItem>
          </List>
          <p>The correct decomposition being:</p>
          <List component="nav">
            <ListItem button>
              <ListItemIcon>#1</ListItemIcon>
              <ListItemText
                disableTypography
                primary={"Return american architects"}
              />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#2</ListItemIcon>
              <ListItemText
                disableTypography
                primary={"Return the bridges desgined by #1"}
              />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#3</ListItemIcon>
              <ListItemText
                disableTypography
                primary={"Return bridge feet length of #2"}
              />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#4</ListItemIcon>
              <ListItemText
                disableTypography
                primary={"Return #2 sorted by #3"}
              />
            </ListItem>
          </List>
          <p>
            The second example shown below also contains a first step that can
            be further decomposed into two steps. Remember that each
            decomposition step should refer to a single operation/condition.
          </p>
          <List component="nav">
            <ListItem button>
              <ListItemText
                primary={
                  "What is the average price for a lesson taught by Janessa Sawayn?"
                }
              />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#1</ListItemIcon>
              <ListItemText
                disableTypography
                style={{ color: color_err }}
                primary={"Return price for lessons taught by Janessa Sawayn"}
              />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#2</ListItemIcon>
              <ListItemText
                disableTypography
                style={{ color: color_err }}
                primary={"Return the average of #1"}
              />
            </ListItem>
          </List>
          <p>The correct decomposition being:</p>
          <List component="nav">
            <ListItem button>
              <ListItemIcon>#1</ListItemIcon>
              <ListItemText disableTypography primary={"Return lessons"} />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#2</ListItemIcon>
              <ListItemText
                disableTypography
                primary={"Return #1 taught by Janessa Sawayn"}
              />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#3</ListItemIcon>
              <ListItemText
                disableTypography
                primary={"Return the price of #2"}
              />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#4</ListItemIcon>
              <ListItemText
                disableTypography
                primary={"Return the average of #3"}
              />
            </ListItem>
          </List>
        </div>
        <div>
          <Divider />
          <Divider />
          <Typography variant="h6" component="h2" id="wrong_order">
            Decomposition order is wrong
          </Typography>
          <p>
            You must think carefully what is the order of the steps you write.
            In the example below the worker's first step refers to the "number
            of rooms". In the original question we are only interested in rooms
            of certain apartments (with code "Gym"). The first step is wrong, as
            it returns the number of all rooms, regardless of their apartments.
            Furthemore, the final step of the decomposition (#3) returns
            apartments rather than counting the number of rooms as required.
          </p>
          <List component="nav">
            <ListItem button>
              <ListItemText
                primary={
                  'Show the total number of rooms of all apartments with facility code "Gym".'
                }
              />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#1</ListItemIcon>
              <ListItemText
                disableTypography
                style={{ color: color_err }}
                primary={"Return total number of rooms"}
              />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#2</ListItemIcon>
              <ListItemText
                disableTypography
                style={{ color: color_err }}
                primary={"Return all apartments"}
              />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#3</ListItemIcon>
              <ListItemText
                disableTypography
                style={{ color: color_err }}
                primary={"Return #2 with facility code Gym"}
              />
            </ListItem>
          </List>
          <p>
            View the correct decomposition, (note the final "aggregation" step):
          </p>
          <List component="nav">
            <ListItem button>
              <ListItemIcon>#1</ListItemIcon>
              <ListItemText disableTypography primary={"Return apartments"} />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#2</ListItemIcon>
              <ListItemText
                disableTypography
                primary={"Return #1 with facility code Gym"}
              />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#3</ListItemIcon>
              <ListItemText
                disableTypography
                primary={"Return the rooms of #2"}
              />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#4</ListItemIcon>
              <ListItemText
                disableTypography
                primary={"Return the number of #3"}
              />
            </ListItem>
          </List>
          <p>
            Each step in the question decomposition must constitute a single
            action. Step #3, "Return played for the LA Lakers" makes no sense
            and is grammatically incorrect. In addition step #4 does not adhere
            to any of the step templates previously defined.
          </p>
          <List component="nav">
            <ListItem button>
              <ListItemText
                primary={
                  "What is height of the Golden State Warriors guard whose father played for the LA Lakers?"
                }
              />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#1</ListItemIcon>
              <ListItemText
                disableTypography
                style={{ color: color_err }}
                primary={"Return height"}
              />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#2</ListItemIcon>
              <ListItemText
                disableTypography
                style={{ color: color_err }}
                primary={"Return Golden State Warriors guard"}
              />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#3</ListItemIcon>
              <ListItemText
                disableTypography
                style={{ color: color_err }}
                primary={"Return played for the LA Lakers"}
              />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#4</ListItemIcon>
              <ListItemText
                disableTypography
                style={{ color: color_err }}
                primary={"Return #1 of #2 whose father #3"}
              />
            </ListItem>
          </List>
          <p>The correct decomposition:</p>
          <List component="nav">
            <ListItem button>
              <ListItemIcon>#1</ListItemIcon>
              <ListItemText
                disableTypography
                primary={"Return Golden State Warriors guard"}
              />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#2</ListItemIcon>
              <ListItemText disableTypography primary={"Return father of #1"} />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#3</ListItemIcon>
              <ListItemText
                disableTypography
                primary={"Return #2 that played for the LA Lakers"}
              />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#4</ListItemIcon>
              <ListItemText
                disableTypography
                primary={"Return #1 whose father is #3"}
              />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#5</ListItemIcon>
              <ListItemText
                disableTypography
                primary={"Return the height of #4"}
              />
            </ListItem>
          </List>
        </div>
        <div>
          <Divider />
          <Divider />
          <Typography variant="h6" component="h2" id="using_and">
            Improper use of 'and' in steps
          </Typography>
          <p>
            In the previous section on "How to write steps" we defined the union
            and intersection operations along with their corresponding
            templates. The word "and" should be reserved for "intersection"
            steps ("both in... <b>and also</b> in..."). When writing a step that
            returns a group of elements ("union" step), the words "or" / ","
            should be used as delimiters instead of "and".
          </p>
          <p>
            In the example below the worker used step #3 to return
            representatives from New York and Indiana. However, the proper
            template suited for the union step is using "or".
          </p>
          <List component="nav">
            <ListItem button>
              <ListItemText
                primary={
                  "What are the life spans of representatives from New York state or Indiana state?"
                }
              />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#1</ListItemIcon>
              <ListItemText
                disableTypography
                style={{ color: color_err }}
                primary={"Return representatives of New York "}
              />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#2</ListItemIcon>
              <ListItemText
                disableTypography
                style={{ color: color_err }}
                primary={"Return representatives of Indiana"}
              />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#3</ListItemIcon>
              <ListItemText
                disableTypography
                style={{ color: color_err }}
                primary={"Return #1 and #2"}
              />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#4</ListItemIcon>
              <ListItemText
                disableTypography
                style={{ color: color_err }}
                primary={"Return life spans of #3"}
              />
            </ListItem>
          </List>
          <p>The correct decomposition, with a correct step #3:</p>
          <List component="nav">
            <ListItem button>
              <ListItemIcon>#1</ListItemIcon>
              <ListItemText
                disableTypography
                primary={"Return representatives"}
              />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#2</ListItemIcon>
              <ListItemText
                disableTypography
                primary={"Return #1 of New York"}
              />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#3</ListItemIcon>
              <ListItemText
                disableTypography
                primary={"Return #1 of Indiana"}
              />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#4</ListItemIcon>
              <ListItemText disableTypography primary={"Return #2 or #3"} />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#5</ListItemIcon>
              <ListItemText
                disableTypography
                primary={"Return life spans of #4"}
              />
            </ListItem>
          </List>
          <p>
            In this example the final step is wrong. Step #4 returns authors of
            papers that are both before 1995 <b>and also</b> after 2002. The
            original question refers to authors of papers before 1995 <b>or</b>{" "}
            after 2002.
          </p>
          <List component="nav">
            <ListItem button>
              <ListItemText
                primary={
                  "Return me the authors who have papers in VLDB conference before 1995 or after 2002 ."
                }
              />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#1</ListItemIcon>
              <ListItemText
                disableTypography
                style={{ color: color_err }}
                primary={"Return papers from VLDB conferences"}
              />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#2</ListItemIcon>
              <ListItemText
                disableTypography
                style={{ color: color_err }}
                primary={"Return #1 before 1995"}
              />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#3</ListItemIcon>
              <ListItemText
                disableTypography
                style={{ color: color_err }}
                primary={"Return #1 after 2002"}
              />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#4</ListItemIcon>
              <ListItemText
                disableTypography
                style={{ color: color_err }}
                primary={"Return authors of both #1 and #2"}
              />
            </ListItem>
          </List>
          <p>The correct decomposition with a correct step #4:</p>
          <List component="nav">
            <ListItem button>
              <ListItemIcon>#1</ListItemIcon>
              <ListItemText disableTypography primary={"Return papers"} />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#2</ListItemIcon>
              <ListItemText
                disableTypography
                primary={"Return #1 from VLDB conferences"}
              />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#3</ListItemIcon>
              <ListItemText
                disableTypography
                primary={"Return #2 before 1995"}
              />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#4</ListItemIcon>
              <ListItemText
                disableTypography
                primary={"Return #2 after 2002"}
              />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#5</ListItemIcon>
              <ListItemText disableTypography primary={"Return #3, #4"} />
            </ListItem>
            <ListItem button>
              <ListItemIcon>#6</ListItemIcon>
              <ListItemText
                disableTypography
                primary={"Return authors of #5"}
              />
            </ListItem>
          </List>
        </div>
      </Fragment>
    )
  },
  {
    title: "Example (previous steps)",
    label: (
      <Fragment>
        <p>
          Referring to previous steps is vital in constructing multi-step
          decompositions. To refer to a previous step we use '#num' where 'num'
          denotes the previous step number. In the example below the third step
          refers to the results of the first two step (secretaries born in
          Alabama), returning "the departments managed by #2".
        </p>
        <List component="nav">
          <ListItem button>
            <ListItemText
              primary={
                "What are the distinct creation years of the departments managed by a secretary born in Alabama state?"
              }
            />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#1</ListItemIcon>
            <ListItemText primary={"Return secretaries"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#2</ListItemIcon>
            <ListItemText primary={"Return #1 born in Alabama state"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#3</ListItemIcon>
            <ListItemText primary={"Return the departments managed by #2"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#4</ListItemIcon>
            <ListItemText primary={"Return distinct creation years of #3"} />
          </ListItem>
        </List>
      </Fragment>
    )
  },
  {
    title: "Example (multiple conditions)",
    label: (
      <Fragment>
        <p>
          Ideally the question decomposition should be constructed such that
          each condition stated in the question is included in a different step.
          In the example below there are three conditions, on the University,
          the research area and on the citations of papers by the authors. The
          first step being a "select" step while steps #2-#3 being "filter"
          steps.
        </p>
        <List component="nav">
          <ListItem button>
            <ListItemText
              primary={
                "Return me authors in the University of Michigan in Databases area whose papers have more than 5000 total citations."
              }
            />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#1</ListItemIcon>
            <ListItemText primary={"Return authors"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#2</ListItemIcon>
            <ListItemText primary={"Return #1 in the University of Michigan"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#3</ListItemIcon>
            <ListItemText primary={"Return #2 in databases areas"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#4</ListItemIcon>
            <ListItemText primary={"Return papers of #3"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#5</ListItemIcon>
            <ListItemText primary={"Return citations of #4"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#6</ListItemIcon>
            <ListItemText primary={"Return the number of #5"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#7</ListItemIcon>
            <ListItemText primary={"Return #3 where #6 is more than 5000"} />
          </ListItem>
        </List>
      </Fragment>
    )
  },
  {
    title: "Example (more conditions)",
    label: (
      <Fragment>
        <p>
          The number of steps for each question decomposition varies according
          to the original question. Questions are usually decomposed to{" "}
          <b>at least</b> two steps. In this example we require 8 steps for our
          question decomposition (Note that the final step is a "union" step).
        </p>
        <List component="nav">
          <ListItem button>
            <ListItemText
              primary={
                "I'd like to see flights from Baltimore to Atlanta that arrive before noon and I'd like to see flights from Denver to Atlanta that arrive before noon."
              }
            />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#1</ListItemIcon>
            <ListItemText primary={"Return flights"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#2</ListItemIcon>
            <ListItemText primary={"Return #1 from Baltimore"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#3</ListItemIcon>
            <ListItemText primary={"Return #2 to Atlanta"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#4</ListItemIcon>
            <ListItemText primary={"Return #3 that arrive before noon"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#5</ListItemIcon>
            <ListItemText primary={"Return #1 from Denver"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#6</ListItemIcon>
            <ListItemText primary={"Return #5 to Atlanta"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#7</ListItemIcon>
            <ListItemText primary={"Return #6 that arrive before noon"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#8</ListItemIcon>
            <ListItemText primary={"Return #4, #7"} />
          </ListItem>
        </List>
      </Fragment>
    )
  },
  {
    title: "Example (aggregation)",
    label: (
      <Fragment>
        <p>
          Many questions require operations such as counting or computing a
          maximum or minimum value over a set of objects. Each aggregation
          operation should be included in its own step. In the example below,
          the fifth step is used to count the number of screens of Landmark
          Theatres.
        </p>
        <List component="nav">
          <ListItem button>
            <ListItemText
              primary={
                "How many screens do Landmark Theatres and Marcus Theatres have combined?"
              }
            />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#1</ListItemIcon>
            <ListItemText primary={"Return Landmark Theatres"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#2</ListItemIcon>
            <ListItemText primary={"Return Marcus Theatres"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#3</ListItemIcon>
            <ListItemText primary={"Return screens of #1"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#4</ListItemIcon>
            <ListItemText primary={"Return screens of #2"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#5</ListItemIcon>
            <ListItemText primary={"Return the number of #3"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#6</ListItemIcon>
            <ListItemText primary={"Return the number of #4"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#7</ListItemIcon>
            <ListItemText primary={"Return the sum of #5 and #6"} />
          </ListItem>
        </List>
      </Fragment>
    )
  },
  {
    title: "Example (aggregation cont.)",
    label: (
      <Fragment>
        <p>
          Each aggregation operation should be included in its own step. In the
          example below, steps #4-#6 are used to perform different aggregations.
        </p>
        <List component="nav">
          <ListItem button>
            <ListItemText
              primary={
                "Return the average, maximum, and minimum budgets in millions for movies made before the year 2000."
              }
            />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#1</ListItemIcon>
            <ListItemText primary={"Return movies"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#2</ListItemIcon>
            <ListItemText primary={"Return #1 made before the year 2000"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#3</ListItemIcon>
            <ListItemText primary={"Return the budgets in millions of #2"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#4</ListItemIcon>
            <ListItemText primary={"Return the average of #3"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#5</ListItemIcon>
            <ListItemText primary={"Return the maximum of #3"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#6</ListItemIcon>
            <ListItemText primary={"Return the minimum of #3"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#7</ListItemIcon>
            <ListItemText primary={"Return #4, #5, #6"} />
          </ListItem>
        </List>
      </Fragment>
    )
  },
  {
    title: "Example (grouping)",
    label: (
      <Fragment>
        <p>
          Certain questions require steps that return pairs of objects (e.g.,
          authors and papers). In this example we need to return the number of
          papers <b>for each author</b>. Steps #4 and #5 actually return pairs
          of authors and the number of papers they have on VLDB and ICDE
          respectively. These steps are necessary if we want to return only
          authors with more papers in VLDB than ICDE.
        </p>
        <List component="nav">
          <ListItem button>
            <ListItemText
              primary={
                "Return me the authors who have more papers on VLDB than ICDE."
              }
            />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#1</ListItemIcon>
            <ListItemText primary={"Return authors"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#2</ListItemIcon>
            <ListItemText primary={"Return VLDB papers"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#3</ListItemIcon>
            <ListItemText primary={"Return ICDE papers"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#4</ListItemIcon>
            <ListItemText primary={"Return the number of #2 for each #1"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#5</ListItemIcon>
            <ListItemText primary={"Return the number of #3 for each #1"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#6</ListItemIcon>
            <ListItemText primary={"Return #1 where #4 is higher than #5"} />
          </ListItem>
        </List>
      </Fragment>
    )
  },
  {
    title: "Example (grouping cont.)",
    label: (
      <Fragment>
        <p>
          In this example step #4 returns the number of "touchdown passes of
          McCown" for each yard line. The "group" step is essential in order to
          later retreive the yard line with exactly 2 passes.
        </p>
        <List component="nav">
          <ListItem button>
            <ListItemText
              primary={
                "From what yard line did Josh McCown throw 2 touchdown passes?"
              }
            />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#1</ListItemIcon>
            <ListItemText primary={"Return Josh McCown"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#2</ListItemIcon>
            <ListItemText primary={"Return touchdown passes of #1"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#3</ListItemIcon>
            <ListItemText primary={"Return the yard lines of #2"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#4</ListItemIcon>
            <ListItemText primary={"Return number of #2 for each #3"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#5</ListItemIcon>
            <ListItemText primary={"Return #3 where #4 is 2"} />
          </ListItem>
        </List>
      </Fragment>
    )
  },
  {
    title: "Example (comparison)",
    label: (
      <Fragment>
        <p>
          When comparing two entites according to a certain attribute (e.g.,
          date) we must first the entities followed by the attributes to be
          compared. In the example below the steps #3-#4 are used to retreive
          the dates of two events. The final step is used to compare the results
          of the previous steps.
        </p>
        <List component="nav">
          <ListItem button>
            <ListItemText
              primary={
                "What event happened first, the act of proscription being outlawed, or new forts being built?"
              }
            />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#1</ListItemIcon>
            <ListItemText
              primary={"Return the act of proscription being outlawed"}
            />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#2</ListItemIcon>
            <ListItemText primary={"Return new forts being built"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#3</ListItemIcon>
            <ListItemText primary={"Return when was #1"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#4</ListItemIcon>
            <ListItemText primary={"Return when was #2"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#5</ListItemIcon>
            <ListItemText primary={"Return which is lowest of #3, #4"} />
          </ListItem>
        </List>
      </Fragment>
    )
  },
  {
    title: "Example (comparison cont.)",
    label: (
      <Fragment>
        <p>
          In the example below the first two steps are used to retreive how old
          is each game. The final step returns the larger of the two groups.
        </p>
        <List component="nav">
          <ListItem button>
            <ListItemText
              primary={
                "What group from the health sector is larger: district or aimag general hospitals?"
              }
            />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#1</ListItemIcon>
            <ListItemText primary={"Return groups from the health sector"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#2</ListItemIcon>
            <ListItemText primary={"Return #1 that is district"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#3</ListItemIcon>
            <ListItemText
              primary={"Return #1 that is aimag general hospital"}
            />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#4</ListItemIcon>
            <ListItemText primary={"Return size of #2"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#5</ListItemIcon>
            <ListItemText primary={"Return size of #3"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#6</ListItemIcon>
            <ListItemText primary={"Return which is highest of #4, #5"} />
          </ListItem>
        </List>
      </Fragment>
    )
  },
  {
    title: "Example (union)",
    label: (
      <Fragment>
        <p>
          In the example below "select" steps #1, #2 return representatives that
          are either from New York or Indiana. Step #4 is a "union" step that
          returns the results of the previous two.
        </p>
        <List component="nav">
          <ListItem button>
            <ListItemText
              primary={
                "What are the life spans of representatives from New York state or Indiana state?"
              }
            />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#1</ListItemIcon>
            <ListItemText primary={"Return representatives"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#2</ListItemIcon>
            <ListItemText primary={"Return #1 from New York State"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#3</ListItemIcon>
            <ListItemText primary={"Return #1 from Indiana state"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#4</ListItemIcon>
            <ListItemText primary={"Return #2, #3"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#5</ListItemIcon>
            <ListItemText primary={"Return the life spans of #4"} />
          </ListItem>
        </List>
      </Fragment>
    )
  },
  {
    title: "Example (union cont.)",
    label: (
      <Fragment>
        <p>
          In this example we are tasked with returning two results. The first
          two steps compute the results while step #6 is the necessary "union"
          step.
        </p>
        <List component="nav">
          <ListItem button>
            <ListItemText
              primary={
                "Find the total number of students and total number of instructors for each department."
              }
            />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#1</ListItemIcon>
            <ListItemText primary={"Return students"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#2</ListItemIcon>
            <ListItemText primary={"Return instructors"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#3</ListItemIcon>
            <ListItemText primary={"Return departments"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#4</ListItemIcon>
            <ListItemText primary={"Return the number of #1 for each #3"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#5</ListItemIcon>
            <ListItemText primary={"Return the number of #2 for each #3"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#6</ListItemIcon>
            <ListItemText primary={"Return #4, #5"} />
          </ListItem>
        </List>
      </Fragment>
    )
  },
  {
    title: "Example (intersection)",
    label: (
      <Fragment>
        <p>
          In the question below we should return only parties that have
          representatives in both New York and in Pennsylvania.
        </p>
        <List component="nav">
          <ListItem button>
            <ListItemText
              primary={
                "Show the parties that have both representatives in New York state and representatives in Pennsylvania state."
              }
            />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#1</ListItemIcon>
            <ListItemText primary={"Return representatives"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#2</ListItemIcon>
            <ListItemText primary={"Return #1 in New York state"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#3</ListItemIcon>
            <ListItemText primary={"Return #1 in Pennsylvania state"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#4</ListItemIcon>
            <ListItemText primary={"Return the parties of both #2 and #3"} />
          </ListItem>
        </List>
      </Fragment>
    )
  },
  {
    title: "Example (discard)",
    label: (
      <Fragment>
        <p>
          In the example, step #3 removes the students who have taken courses
          from the Biology department.
        </p>
        <List component="nav">
          <ListItem button>
            <ListItemText
              primary={
                "Find the name of students who didn't take any course from Biology department."
              }
            />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#1</ListItemIcon>
            <ListItemText primary={"Return courses"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#2</ListItemIcon>
            <ListItemText primary={"Return #1 from biology department"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#3</ListItemIcon>
            <ListItemText primary={"Return students of #2"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#4</ListItemIcon>
            <ListItemText primary={"Return students besides #3"} />
          </ListItem>
        </List>
      </Fragment>
    )
  },
  {
    title: "Example (sorting)",
    label: (
      <Fragment>
        <p>
          The final step of the example sorts the result of step #2 in the
          specified order.
        </p>
        <List component="nav">
          <ListItem button>
            <ListItemText
              primary={
                "Show the name of all bridges that was designed by american architects, and sort the result by the bridge feet length."
              }
            />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#1</ListItemIcon>
            <ListItemText primary={"Return american architects"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#2</ListItemIcon>
            <ListItemText
              primary={"Return the name of bridges designed by #1"}
            />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#3</ListItemIcon>
            <ListItemText primary={"Return #2 sorted by bridge feet length"} />
          </ListItem>
        </List>
      </Fragment>
    )
  },
  {
    title: "Example (is true)",
    label: (
      <Fragment>
        <p>
          Certain questions require us to verify whether a certain condition
          holds, or not. Such questions should contain an "is true" step, such
          as step #5 below.
        </p>
        <List component="nav">
          <ListItem button>
            <ListItemText
              primary={
                "Did Lostalone and Guster have the same number of members?"
              }
            />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#1</ListItemIcon>
            <ListItemText primary={"Return Lostalone"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#2</ListItemIcon>
            <ListItemText primary={"Return Guster"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#3</ListItemIcon>
            <ListItemText primary={"Return members of #1"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#4</ListItemIcon>
            <ListItemText primary={"Return members of #2"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#5</ListItemIcon>
            <ListItemText primary={"Return the number of #3"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#6</ListItemIcon>
            <ListItemText primary={"Return the number of #4"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#7</ListItemIcon>
            <ListItemText primary={"Return if #5 is the same as #6"} />
          </ListItem>
        </List>
      </Fragment>
    )
  },
  {
    title: "Example (is true cont.)",
    label: (
      <Fragment>
        <p>
          In the example below we have two conditions which we need to express.
          The first condition regarding the cube's color and the second,
          regarding its material. Both conditions are expressed in steps #7 and
          #8. At the final step we return both the condition results, as asked
          in the question.
        </p>
        <List component="nav">
          <ListItem button>
            <ListItemText
              primary={
                "Is the cube the same color or material as the other small objects?"
              }
            />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#1</ListItemIcon>
            <ListItemText primary={"Return the cube"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#2</ListItemIcon>
            <ListItemText primary={"Return small objects besides #1"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#3</ListItemIcon>
            <ListItemText primary={"Return the color of #1"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#4</ListItemIcon>
            <ListItemText primary={"Return the color of #2"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#5</ListItemIcon>
            <ListItemText primary={"Return the material of #1"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#6</ListItemIcon>
            <ListItemText primary={"Return the material of #2"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#7</ListItemIcon>
            <ListItemText primary={"Return is #3 the same as #4"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#8</ListItemIcon>
            <ListItemText primary={"Return is #5 the same as #6"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#9</ListItemIcon>
            <ListItemText primary={"Return #7 or #8"} />
          </ListItem>
        </List>
      </Fragment>
    )
  },
  {
    title: "Example (arithmetic)",
    label: (
      <Fragment>
        <p>
          Decompositions sometimes require performing an arithmetic operation
          such as addition, subtraction, multiplication or division. In the
          example below we need to subtract the number of men from the number of
          women.
        </p>
        <List component="nav">
          <ListItem button>
            <ListItemText
              primary={"How many more zebras wetre there compared to tigers?"}
            />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#1</ListItemIcon>
            <ListItemText primary={"Return zebras"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#2</ListItemIcon>
            <ListItemText primary={"Return tigers"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#3</ListItemIcon>
            <ListItemText primary={"Return the number of #1"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#4</ListItemIcon>
            <ListItemText primary={"Return the number of #2"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#5</ListItemIcon>
            <ListItemText primary={"Return the difference of #3 and #4"} />
          </ListItem>
        </List>
      </Fragment>
    )
  },
  {
    title: "End of instructions",
    label: (
      <Fragment>
        <p>
          Congratulations on reviewing the TDT instruction manual. After fully
          understanding the scope of the task, its step templates, common
          pitfalls and numerous examples you are ready to enter your question id
          and start writing. When you are done, press 'Submit' to receive your
          survey code. We strongly suggest you continue to review the 'How to
          write steps' and 'Common pitfalls' sections as you are writing your
          decomposition.
        </p>
        <p>Good luck!</p>
      </Fragment>
    )
  }
];

class ProgressMobileStepper extends React.Component {
  state = {
    activeStep: 0
  };

  handleNext = () => {
    this.setState(state => ({
      activeStep: state.activeStep + 1
    }));
  };

  handleBack = () => {
    this.setState(state => ({
      activeStep: state.activeStep - 1
    }));
  };

  render() {
    const { classes, theme } = this.props;
    const { activeStep } = this.state;
    const maxSteps = tutorialSteps.length;

    return (
      <div className={classes.root}>
        <MobileStepper
          variant="progress"
          style={style.Stepper}
          steps={maxSteps}
          position="static"
          activeStep={activeStep}
          className={classes.mobileStepper}
          nextButton={
            <Button
              size="small"
              onClick={this.handleNext}
              disabled={activeStep === maxSteps - 1}
            >
              Next
              {theme.direction === "rtl" ? (
                <KeyboardArrowLeft />
              ) : (
                <KeyboardArrowRight />
              )}
            </Button>
          }
          backButton={
            <Button
              size="small"
              onClick={this.handleBack}
              disabled={activeStep === 0}
            >
              {theme.direction === "rtl" ? (
                <KeyboardArrowRight />
              ) : (
                <KeyboardArrowLeft />
              )}
              Back
            </Button>
          }
        />
        <Card style={style.Card} className={classes.card}>
          <CardContent>
            <Typography gutterBottom variant="h5" component="h2">
              {tutorialSteps[activeStep].title}
            </Typography>
            <Typography component="p">
              {tutorialSteps[activeStep].label}
            </Typography>
          </CardContent>
        </Card>
      </div>
    );
  }
}

ProgressMobileStepper.propTypes = {
  classes: PropTypes.object.isRequired,
  theme: PropTypes.object.isRequired
};

export default withStyles(styles, { withTheme: true })(ProgressMobileStepper);
