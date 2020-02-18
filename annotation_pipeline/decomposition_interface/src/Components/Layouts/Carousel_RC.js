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
            <font color="red">
              Note that the decomposition instructions have been changed! Please
              review the updated decomposition instructions next.
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
            <li>Return the yards of field goals by Phil Dawson</li>
            <li>Return the longest of the yards</li>
            <li>Return the shortest of the yards</li>
            <li>Return the their difference</li>
          </ol>
          Note that this is actually a numbered list of actions that refer to
          results of previous steps. Hence we can (and will) use{" "}
          <b>references to previous steps</b>:
          <ol>
            <li>Return yards of field goals of Phil Dawson</li>
            <li>
              Return the longest of <b>#1</b>
            </li>
            <li>
              Return the shortest of <b>#1</b>
            </li>
            <li>
              Return the difference of <b>#2</b> and <b>#3</b>
            </li>
          </ol>
        </p>
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
          <h3>
            <font color="red">New RC decomposition</font>
          </h3>
          The key difference of this task from the original TDT decomposition is
          in the less granular nature of steps. We replace the old SELECT,
          operator with a new operator, <b>FIND</b> which has the properties of
          SELECT+PROJECT+FILTER combined. The following examples will help
          demonstrate the level of granualarity required from our RC
          decompositions.
        </p>
        <p>
          <b>Vocabulary: </b> when filling out a step you are restricted in the
          words that you may use. You vocabulary will consist of all words
          appearing in the original questions in addition to relevant stop words
          and operations (more than, at least, where, of, is, etc.).
        </p>
        <p>
          <b>Click 'Next' to review decomposition examples</b>
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
              <Typography style={style.Typography}>
                <font color="red">FIND</font>
              </Typography>
              <Typography style={{ flexBasis: myFlex }}>
                Return [noun phrase]
              </Typography>
              <Typography>
                Return [American sociologist born on February 23, 1868 that was
                a recipient of the Lenin Peace Prize]
              </Typography>
            </ExpansionPanelSummary>
            <ExpansionPanelDetails>
              <Typography>
                A select step is used to return a phrase describing a single
                object in the question. There are no references to previous
                steps in a select step. Examples of select steps:
                <li>Return year The Ottoman commander of Medina surrendered</li>
                <li>Return when was Cameron sent to assassinate George II</li>
                <li>Return the stronghold on the island of Basilan</li>
                <li>Return Italian-Austrailian man born on August 6, 1955</li>
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
    title: "Example (previous steps)",
    label: (
      <Fragment>
        <p>
          Referring to previous steps is vital in constructing multi-step
          decompositions. To refer to a previous step we use '#num' where 'num'
          denotes the previous step number. In the example below the third step
          refers to the results of the first two steps (longest touchdown),
          returning "in which quarter was #2".
        </p>
        <List component="nav">
          <ListItem button>
            <ListItemText
              primary={
                "In which quarter was the longest touchdown pass of the game?"
              }
            />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#1</ListItemIcon>
            <ListItemText primary={"Return touchdown passes of the game "} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#2</ListItemIcon>
            <ListItemText primary={"Return longest of #1"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#3</ListItemIcon>
            <ListItemText primary={"Return in which quarter was #2"} />
          </ListItem>
        </List>
      </Fragment>
    )
  },
  {
    title: "Example (finding entities)",
    label: (
      <Fragment>
        <p>
          Many of the questions require us first to find a specific entity and
          then return a certain attribute of it. In the example below we must
          first find the "American sociologist born on February 23, 1868 that
          was a recipient of the Lenin Peace Prize" and only then can we answer
          the question by returning "the association #1 was co founder of".
        </p>
        <List component="nav">
          <ListItem button>
            <ListItemText
              primary={
                "This American sociologist born on February 23, 1868 was a recipient of the Lenin Peace Prize and also one of the co-founders of what association?"
              }
            />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#1</ListItemIcon>
            <ListItemText
              primary={
                "Return American sociologist born on February 23, 1868 that was a recipient of the Lenin Peace Prize"
              }
            />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#2</ListItemIcon>
            <ListItemText primary={"Return association #1 was co-founder of"} />
          </ListItem>
        </List>
      </Fragment>
    )
  },
  {
    title: "Example (more finding entities)",
    label: (
      <Fragment>
        <p>
          To answer the question below we must first find the states bordering
          Virginia. Of these states we then return the one which held the 107th
          legislative session of Congress.
        </p>
        <List component="nav">
          <ListItem button>
            <ListItemText
              primary={
                "Which state that borders Virginia held the 107th legislative session of the United States Congress?"
              }
            />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#1</ListItemIcon>
            <ListItemText primary={"Return states that border Virginia"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#2</ListItemIcon>
            <ListItemText
              primary={
                "Return #1 that held the 107th legislative session of the United States Congress"
              }
            />
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
          the third step is used to count the number of books written by the
          author.
        </p>
        <List component="nav">
          <ListItem button>
            <ListItemText
              primary={
                "The Foreigner universe is a fictional universe created by an author that has written approximately how many books?"
              }
            />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#1</ListItemIcon>
            <ListItemText primary={"Return author of The Foreigner universe"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#2</ListItemIcon>
            <ListItemText primary={"Return books written by #1"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#3</ListItemIcon>
            <ListItemText primary={"Return the number of #2"} />
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
          example below, steps #3-#5 are used to perform different aggregations.
        </p>
        <List component="nav">
          <ListItem button>
            <ListItemText
              primary={
                "How many Hindi speakers outside of India are in Nepal and Suriname?"
              }
            />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#1</ListItemIcon>
            <ListItemText primary={"Return Hindi speakers in Nepal"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#2</ListItemIcon>
            <ListItemText primary={"Return Hindi speakers in Suriname"} />
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
            <ListItemText primary={"Return sum of #3 and #4"} />
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
          In this example step #3 returns the number of "memberships registered
          in 2016" for each branch. The "group" step is essential in order to
          later retreive the branch with the highest number of memberships.
        </p>
        <List component="nav">
          <ListItem button>
            <ListItemText
              primary={
                "What is the open year of the branch with most number of memberships registered in 2016?"
              }
            />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#1</ListItemIcon>
            <ListItemText primary={"Return branches"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#2</ListItemIcon>
            <ListItemText
              primary={"Return memberships registered in 2016 of #1"}
            />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#3</ListItemIcon>
            <ListItemText primary={"Return the number of #2 for each #1"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#4</ListItemIcon>
            <ListItemText primary={"Return the #1 where #3 is highest"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#5</ListItemIcon>
            <ListItemText primary={"Return the open year of #4"} />
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
          When comparing two objects according to a certain attribute (e.g.,
          height) we must first return the attributes to be compared. In the
          example below the first two steps are used to retreive the height of
          two mountains. The final step is used to compare the results of the
          previous steps.
        </p>
        <List component="nav">
          <ListItem button>
            <ListItemText
              primary={"Which mountain is higher, Manaslu or Jengish Chokusu?"}
            />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#1</ListItemIcon>
            <ListItemText primary={"Return how high is Manaslu"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#2</ListItemIcon>
            <ListItemText primary={"Return how high is Jengish Chokusu"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#3</ListItemIcon>
            <ListItemText
              primary={"Return which is higher of #1, #2"}
            />
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
          is each game. The third steps returns the oldest of the two.
        </p>
        <List component="nav">
          <ListItem button>
            <ListItemText
              primary={
                "Which game is the oldest, Ticket to Ride or King of Tokyo?"
              }
            />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#1</ListItemIcon>
            <ListItemText primary={"Return how old is Ticket to Ride"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#2</ListItemIcon>
            <ListItemText primary={"Return how old is King of Tokyo"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#3</ListItemIcon>
            <ListItemText
              primary={"Return which is highest of #1, #2"}
            />
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
          are either from New York or Indiana. Step #3 is a "union" step that
          return results of the previous two.
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
          two steps compute the results while step #3 is the necessary "union"
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
            <ListItemText
              primary={"Return the number of #1 for each department"}
            />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#4</ListItemIcon>
            <ListItemText
              primary={"Return the number of #2 for each department"}
            />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#5</ListItemIcon>
            <ListItemText primary={"Return #3, #4"} />
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
          In the example, step #2 removes the PhD certification from the rest of
          the results of step #1.
        </p>
        <List component="nav">
          <ListItem button>
            <ListItemText
              primary={
                "Nell Hodgson Woodruff School of Nursing awards what certification for a doctoral program, other than a PhD?"
              }
            />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#1</ListItemIcon>
            <ListItemText
              primary={
                "Return doctoral program certifications awarded by Nell Hodgson Woodruff School of Nursing"
              }
            />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#2</ListItemIcon>
            <ListItemText primary={"Return #2 besides PhD"} />
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
            <ListItemText primary={"Return members of Lostalone"} />
          </ListItem>
          <ListItem button>
            <ListItemIcon>#2</ListItemIcon>
            <ListItemText primary={"Return members of Guster"} />
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
            <ListItemText primary={"Return if #3 is the same as #4"} />
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
