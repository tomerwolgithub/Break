

class DecomposeRule(object):
    def __init__(self, start_offset=1, end_offset=2):
        self.question = None
        self.decomposition_offset = None
        self.is_decomposed = False
        self.check_res = None

        self.start_offset = start_offset
        self.end_offset = end_offset

    def check(self, question, decomposition_offset):
        self.question = question
        self.decomposition_offset = decomposition_offset
        self.is_decomposed = False
        self.check_res = self._check()
        return self.check_res

    def decompose(self):
        assert self.question and self.check_res and not self.is_decomposed
        self.is_decomposed = True
        return self._decompose()

    def _check(self):
        raise NotImplementedError

    def _decompose(self):
        raise NotImplementedError


class DecomposeRuleSinglePrep(DecomposeRule):
    """
    Positive "of" example: "the 1996 coach of the team owned by Jerry Jones"
    Negative "of" example: "The author in the University of Michigan in Databases area"
    First "for" example: "the name and open year for the branch with most number of memberships registered in 2016"
    Second "for" example: "the average price for a lesson taught by Janessa Sawayn"
    """
    def __init__(self, *args, **kwargs):
        super(DecomposeRuleSinglePrep, self).__init__(*args, **kwargs)
        self.prep_index = None
        self.prep_direction = None

        self.forward_preps = ["of", "for", "among"]
        self.backward_preps = ["on", "to", "from", "with"]

    def _is_recursive_call(self, i):
        return self.question[i-1].text.startswith("@@")

    def _check_index(self, i):
        res1 = self.question[i].text in ["of", "for", "with"] and \
               self.question[i].ent_type_ == "" and \
               self.question[i].dep_ == "prep" and \
               self.question[i + 1].dep_ in ["det", "predet"] and \
               self.question[i + 1].head.dep_ == "pobj" and \
               self.question[i + 1].head.head.i == i

        res2 = self.question[i].text in ["of", "for", "among", "on", "to", "from", "with"] and \
               self.question[i].ent_type_ == "" and \
               self.question[i].dep_ == "prep" and \
               self.question[i + 1].dep_ == "pobj" and \
               self.question[i + 1].head.i == i and \
               self.question[i - 1].pos_ != "VERB"

        return (res1 or res2) and not self._is_recursive_call(i)

    def _check(self):
        self.prep_index = None
        self.prep_direction = None

        for i in range(self.start_offset, len(self.question) - self.end_offset):
            if self._check_index(i):
                self.prep_index = i
                if self.question[i].text in self.forward_preps:
                    self.prep_direction = "forward"
                else:
                    self.prep_direction = "backward"

                return True

        return False

    def _decompose(self):
        if self.prep_direction == "forward":
            return [self.question[self.prep_index+1:].text,
                    self.question[:self.prep_index+1].text + " @@{}@@".format(self.decomposition_offset)]
        else:
            return [self.question[:self.prep_index].text,
                    "@@{}@@ ".format(self.decomposition_offset) + self.question[self.prep_index:].text]


class DecomposeRuleSuperlative(DecomposeRule):
    """
    Example: "what is the size of the largest state in the usa"
    """
    def __init__(self, *args, **kwargs):
        super(DecomposeRuleSuperlative, self).__init__(*args, **kwargs)
        self.superlative_index = None

    def _check_index(self, i):
        res1 = self.question[i].tag_ == "JJS" and \
               self.question[i].dep_ == "amod"

        res2 = self.question[i-1].tag_ == "RBS" and \
               self.question[i].tag_ == "JJ" and \
               self.question[i].dep_ == "amod"

        return res1 or res2

    def _check(self):
        self.superlative_index = None

        for i in range(self.start_offset, len(self.question) - self.end_offset):
            if self._check_index(i):
                self.superlative_index = i
                return True

        return False

    def _decompose(self):
        return [self.question[self.superlative_index+1:].text,
                self.question[:self.superlative_index+1].text + " @@{}@@".format(self.decomposition_offset)]


class DecomposeRuleConjunction(DecomposeRule):
    """
    Example: "Who held their governmental position from 1786 and was the British General of the Revolutionary War?"
    """
    def __init__(self, *args, **kwargs):
        super(DecomposeRuleConjunction, self).__init__(*args, **kwargs)
        self.conjunction_index = None

    def _check(self):
        self.conjunction_index = None

        for i in range(len(self.question) - self.end_offset):
            if self.question[i].text == "and" and \
                    self.question[i].dep_ == "cc" and \
                    self.question[i + 1].dep_ == "conj" and \
                    self.question[i + 1].pos_ == "VERB" and \
                    self.question[i].head.pos_ == "VERB" and \
                    self.question[i].head.i == self.question[i + 1].head.i:
                self.conjunction_index = i
                return True

        return False

    def _decompose(self):
        head_index = self.question[self.conjunction_index].head.i
        return [self.question[:head_index].text + " " + self.question[self.conjunction_index+1:].text,
                "@@{}@@ ".format(self.decomposition_offset) + self.question[head_index:self.conjunction_index].text]


class DecomposeRuleSubjDoHave(DecomposeRule):
    """
    Example: "What movie with film character named Mr. Woodson did Tupac star in?"
    """
    def __init__(self, size_gap=4, *args, **kwargs):
        super(DecomposeRuleSubjDoHave, self).__init__(*args, **kwargs)
        self.size_gap = size_gap
        self.do_index = None
        self.nsubj_index = None
        self.nsubj_end_index = None

    def _check_nsubj_complexity(self, i):
        for j in range(i+1, self.question[i].head.i):
            res1 = self.question[j].pos_ == "ADP" and \
                   self.question[j].text != "of"

            res2 = self.question[i].head.i - j > 2 and \
                   self.question[j].dep_ == "acl" and \
                   self.question[j+1].dep_ == "agent"

            if res1 or res2:
                self.nsubj_end_index = j-1
                return True

        return False

    def _check_index(self, i):
        res = self.question[i].lemma_ in ["do", "have"] and \
              self.question[i].pos_ == "VERB" and \
              (self.question[self.nsubj_index].head.i == i or
               self.question[self.nsubj_index].head.i == self.question[i].head.i)

        return res

    def _check(self):
        self.do_index = None
        self.nsubj_index = None
        self.nsubj_end_index = None

        for i in range(min(self.size_gap, len(self.question))):
            if self.question[i].pos_ == "NOUN" and \
                    self.question[i].dep_ == "nsubj" and \
                    self._check_nsubj_complexity(i):
                left_heads = [self.question[j].head.i > i for j in range(i)]
                if sum(left_heads) == 0:
                    self.nsubj_index = i

        if self.nsubj_index is not None:
            for i in range(self.nsubj_end_index+1, len(self.question) - self.end_offset):
                if self._check_index(i):
                    self.do_index = i
                    return True

        return False

    def _decompose(self):
        return [self.question[:self.nsubj_end_index+1].text + " " + self.question[self.do_index+1:].text,
                "@@{}@@ ".format(self.decomposition_offset) + self.question[self.nsubj_end_index+1:self.do_index].text]


class DecomposeRuleDoSubj(DecomposeRule):
    """
    Example: "how many states in the us does the shortest river run through"
    """
    def __init__(self, *args, **kwargs):
        super(DecomposeRuleDoSubj, self).__init__(*args, **kwargs)
        self.verb_index = None
        self.do_index = None

    def _check_index(self, i, nsubj_index, aux_index):
        if nsubj_index is None:
            nsubj_right_pos = []
        else:
            nsubj_right_pos = [x.pos_ for x in self.question[nsubj_index].rights]

        res = self.question[i].pos_ == "VERB" and \
              nsubj_index is not None and \
              aux_index is not None and \
              nsubj_index > aux_index and \
               "ADP" in nsubj_right_pos and \
              not self._is_recursive_call(i)

        return res

    def _is_recursive_call(self, i):
        return self.question[i-1].text.startswith("@@")

    def _check(self):
        self.verb_index = None
        self.do_index = None

        for i in range(len(self.question)):
            lefts = [x for x in self.question[i].lefts]
            nsubj_index, aux_index = None, None

            for left in lefts:
                if left.dep_ == "nsubj":
                    nsubj_index = left.i
                elif left.dep_ == "aux" and left.lemma_ == "do":
                    aux_index = left.i

            if self._check_index(i, nsubj_index, aux_index):
                self.verb_index = i
                self.do_index = aux_index
                return True

        return False

    def _decompose(self):
        return [self.question[self.do_index+1:self.verb_index].text,
                self.question[:self.do_index+1].text + " @@{}@@ ".format(self.decomposition_offset) +
                self.question[self.verb_index:].text]


class DecomposeRuleRelcl(DecomposeRule):
    """
    Example: "movie starring Zac Efron that has a character named Owen Lars"
    Second example: "height of the Golden State Warriors guard whose father played for the LA Lakers"
    """
    def __init__(self, *args, **kwargs):
        super(DecomposeRuleRelcl, self).__init__(*args, **kwargs)
        self.relative_pronoun_index = None
        self.relcl_index = None
        self.relative_pronouns = ["that", "whose", "who", "whom", "which"]

    def _is_recursive_call(self, i):
        return self.question[i-1].text.startswith("@@")

    def _check_index(self, i):
        res = self.question[i].dep_ in ["relcl", "poss"] and \
              self.question[i].left_edge.text in self.relative_pronouns and \
              not self._is_recursive_call(self.question[i].left_edge.i)

        return res

    def _check(self):
        self.relative_pronoun_index = None
        self.relcl_index = None

        for i in range(self.start_offset, len(self.question) - self.end_offset):
            if self._check_index(i):
                self.relative_pronoun_index = self.question[i].left_edge.i
                self.relcl_index = i
                return True

        return False

    def _decompose(self):
        return [self.question[:self.relative_pronoun_index].text,
                "@@{}@@ ".format(self.decomposition_offset) + self.question[self.relative_pronoun_index:].text]

    def check_relcl_contains_index(self, i):
        return self.question[self.relcl_index].head.i < i < self.relcl_index


class DecomposeRuleHowMany(DecomposeRule):
    """
    Positive example: "How many yards was the longest touchdown of the game?"
    Negative example: "How many more red objects are there than blue objects?"
    """
    def __init__(self, *args, **kwargs):
        super(DecomposeRuleHowMany, self).__init__(*args, **kwargs)
        self.nsubj_index = None
        self.aux_index = None

    def _check(self):
        self.nsubj_index = None
        self.aux_index = None

        # check this is a "how many" question
        if not self.question.text.lower().startswith("how many") or \
                self.question.text.lower().startswith("how many more"):
            return False

        # look for nsubj and auxiliary tokens
        if self.question[1].head.dep_ == "nsubj" and \
                self.question[1].head.head.pos_ == "VERB":
            self.nsubj_index = self.question[1].head.i
            if self.question[1].head.head.dep_ == "aux" and \
                    self.question[1].head.head.pos_ == "VERB" and \
                    self.question[1].head.head.lemma_ == "do":
                self.aux_index = self.question[1].head.head.i
        else:
            head = self.question[1].head.head
            candidates = [x for x in head.lefts]
            for candidate in candidates:
                if candidate.dep_ == "nsubj" and candidate.head.pos_ == "VERB":
                    self.nsubj_index = candidate.i
                if candidate.dep_ == "aux" and candidate.pos_ == "VERB" and \
                        candidate.lemma_ == "do":
                    self.aux_index = candidate.i

        if self.nsubj_index is None:
            return False

        return True

    def _decompose(self):
        decomposed = []

        # case 1: aux + nsubj
        if self.aux_index is not None:
            decomposed.append(self.question[2:self.aux_index].text + " " +
                              self.question[self.aux_index + 1:].text)

        # case 2: to-be verb nsubj
        elif self.question[self.nsubj_index].head.lemma_ == "be":
            be_index = self.question[self.nsubj_index].head.i
            if be_index + 1 == len(self.question):
                prep_string = ""
                post_prep_string = ""
            elif self.question[be_index+1].dep_ == "prep":
                prep_string = " "
                post_prep_string = self.question[be_index + 1:].text
            else:
                prep_string = " of "
                post_prep_string = self.question[be_index + 1:].text

            decomposed.append(self.question[2:be_index].text + prep_string +
                              post_prep_string)

        # case 3: non-to-be verb nsubj
        else:
            decomposed.append(self.question[2:].text)

        decomposed.append("the number of @@{}@@".format(self.decomposition_offset))
        return decomposed


class DecomposeRuleBeAuxpass(DecomposeRule):
    """
    Example: "which former member of the pittsburgh pirates was nicknamed 'the cobra'"
    Second example: "government position was held by the woman who portrayed
                        Corliss Archer in the film Kiss and Tell"
    """
    def __init__(self, *args, **kwargs):
        super(DecomposeRuleBeAuxpass, self).__init__(*args, **kwargs)
        self.be_index = None

    def get_leftmost_child(self, i):
        most_direct_left = None
        lefts = [x for x in self.question[i].head.lefts]
        if len(lefts) > 0:
            most_direct_left = lefts[0]

        return most_direct_left

    def _check_index(self, i):
        most_direct_left = self.get_leftmost_child(i)

        res = self.question[i].lemma_ == "be" and \
              self.question[i].pos_ == "VERB" and \
              self.question[i].dep_ == "auxpass" and \
              self.question[i].head.pos_ == "VERB" and \
              most_direct_left is not None and most_direct_left.dep_ == "nsubjpass"

        return res

    def _check(self):
        self.be_index = None

        for i in range(len(self.question)):
            if self._check_index(i):
                self.be_index = i
                return True

        return False

    def _decompose(self):
        head_index = self.question[self.be_index].head.i
        if head_index+1 < len(self.question) and \
                self.question[head_index+1].pos_ == "ADP":
            split_index = head_index + 2
            if head_index+2 < len(self.question) and \
                    self.question[head_index+2].text in ["what", "which"]:    # e.g. in which, of what
                split_index += 1
            return [self.question[split_index:].text,
                    self.question[:self.be_index].text + " "
                    + self.question[self.be_index+1:head_index+2].text
                    + " @@{}@@ ".format(self.decomposition_offset)]
        else:
            return [self.question[:self.be_index].text,
                    "@@{}@@ ".format(self.decomposition_offset) + self.question[self.be_index + 1:].text]


class DecomposeRuleBeRoot(DecomposeRule):
    """
    Example: "how many objects smaller than the matte object are silver"
    """
    def __init__(self, *args, **kwargs):
        super(DecomposeRuleBeRoot, self).__init__(*args, **kwargs)
        self.be_index = None
        self.left_index = None
        self.right_index = None

    def get_leftmost_child(self, i):
        most_direct_left = None
        lefts = [x for x in self.question[i].head.lefts]
        if len(lefts) > 0:
            most_direct_left = lefts[0]

        return most_direct_left

    def get_rightmost_child(self, i):
        most_direct_right = None
        rights = [x for x in self.question[i].head.rights]
        if len(rights) > 0:
            most_direct_right = rights[-1]

        return most_direct_right

    def _check_index(self, i, most_direct_left, most_direct_right):
        res = self.question[i].lemma_ == "be" and \
              self.question[i].pos_ == "VERB" and \
              self.question[i].dep_ == "ROOT" and \
              (most_direct_left is not None and most_direct_left.dep_ == "csubj" or
               most_direct_right is not None and most_direct_right.dep_ == "advcl")

        return res

    def _check(self):
        self.be_index = None
        self.left_index = None
        self.right_index = None

        for i in range(len(self.question)):
            most_direct_left = self.get_leftmost_child(i)
            most_direct_right = self.get_rightmost_child(i)

            if self._check_index(i, most_direct_left, most_direct_right):
                assert most_direct_left is not None or most_direct_right is not None
                self.be_index = i
                if most_direct_left is not None:
                    self.left_index = most_direct_left.i
                else:
                    self.right_index = most_direct_right.i
                return True

        return False

    def _decompose(self):
        assert self.left_index is not None or self.right_index is not None

        if self.left_index is not None:
            return [self.question[self.left_index:self.be_index].text,
                    self.question[:self.left_index].text +
                    " @@{}@@ ".format(self.decomposition_offset) +
                    self.question[self.be_index+1:].text]
        else:
            return [self.question[self.be_index+1:self.right_index].text,
                    self.question[:self.be_index].text +
                    " @@{}@@ ".format(self.decomposition_offset)
                    + self.question[self.right_index:].text]


class DecomposeRuleMultiPrep(DecomposeRule):
    """
    Example: "a us air flight from toronto to san diego with a stopover in denver"
    """
    def __init__(self, *args, **kwargs):
        super(DecomposeRuleMultiPrep, self).__init__(*args, **kwargs)
        self.prep_indices = None

    def _is_recursive_call(self, i):
        return self.question[i].text.startswith("@@")

    def _check_index(self, i):
        rights = [r for r in self.question[i].rights]
        num_rights = len(rights)
        num_prep = len([r for r in rights if r.dep_ == "prep"])
        num_adp = len([r for r in rights if r.pos_ in ["ADP", "PART"]])

        if num_rights != num_prep or num_rights != num_adp or num_rights == 0:
            return False

        res = num_prep > 1 and not self._is_recursive_call(i)

        return res

    def _check(self):
        self.prep_indices = None

        for i in range(len(self.question) - self.end_offset):
            if self._check_index(i):
                rights = [r for r in self.question[i].rights]
                self.prep_indices = [r.i for r in rights]
                if self.question[i].pos_ == "VERB" and i > 0:
                    self.prep_indices[0] -= 1

                return True

        return False

    def _decompose(self):
        decomposition = [self.question[:self.prep_indices[0]].text]
        idx = self.prep_indices + [len(self.question)]

        for i in range(len(idx)-1):
            decomposition.append("@@{}@@ ".format(self.decomposition_offset + i) +
                                 self.question[idx[i]:idx[i+1]].text)

        return decomposition


class DecomposeRuleAclVerb(DecomposeRule):
    """
    Example: "movie starring Zac Efron that has a character named Owen Lars"
    Second example: "the number of papers in VLDB conference containing keyword \" Information Retrieval \""
    """
    def __init__(self, *args, **kwargs):
        super(DecomposeRuleAclVerb, self).__init__(*args, **kwargs)
        self.verb_index = None

    def _is_recursive_call(self, i):
        return self.question[i-1].text.startswith("@@")

    def _check_index(self, i):
        res = self.question[i].dep_ == "acl" and \
              self.question[i].tag_ == "VBG" and \
              not self._is_recursive_call(i)

        return res

    def _check(self):
        self.verb_index = None

        for i in range(self.start_offset, len(self.question) - self.end_offset):
            if self._check_index(i):
                self.verb_index = i
                return True

        return False

    def _decompose(self):
        right_end_index = self.question[self.verb_index].right_edge.i

        return [self.question[:self.verb_index].text + " " + self.question[right_end_index+1:].text,
                "@@{}@@ ".format(self.decomposition_offset) + self.question[self.verb_index:right_end_index+1].text]

