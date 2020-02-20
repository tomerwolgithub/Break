
import re

from model.rule_based.decompose_rules import *
from model.model_base import ModelBase


class RuleBasedModel(ModelBase):
    def __init__(self):
        super(RuleBasedModel, self).__init__()
        self.prefixes_to_remove = ["what is", "what are", "who is", "who are", "who was", "who were",
                                   "in what", "in which",
                                   "show me", "return me", "give me",
                                   "can you list", "i'd like to see", "i would like", "do you have",
                                   "what", "which", "list", "show", "return", "find"]
        # TODO: consider keeping question marks, which improve tagger accuracy
        #  (e.g. "Where did the illustrator of \"De Divina Proportione\" die?").
        self.suffixes_to_remove = ["?", "?\"", ".", "please"]
        self.infixes_to_substitute = [
            ("are there", "(.*are) there(.*)", lambda x: x.group(1) + x.group(2)),
            ("were there", "(.*were) there(.*)", lambda x: x.group(1) + x.group(2))
        ]

        self.rules = {"single_prep": DecomposeRuleSinglePrep(),
                      "superlative": DecomposeRuleSuperlative(),
                      "conjunction": DecomposeRuleConjunction(),
                      "subj_do_have": DecomposeRuleSubjDoHave(),
                      "do_subj": DecomposeRuleDoSubj(),
                      "relcl": DecomposeRuleRelcl(),
                      "how_many": DecomposeRuleHowMany(),
                      "be_auxpass": DecomposeRuleBeAuxpass(),
                      "be_root": DecomposeRuleBeRoot(),
                      "multi_prep": DecomposeRuleMultiPrep(),
                      "acl_verb": DecomposeRuleAclVerb()}

    def _clean(self, question):
        """Simplify the question by removing extra unnecessary parts of it, if exist."""
        for prefix in self.prefixes_to_remove:
            if question.lower().startswith(prefix):
                question = question[len(prefix):].strip()
                break

        for suffix in self.suffixes_to_remove:
            if question.lower().endswith(suffix):
                question = question[:-len(suffix)].strip()
                break

        for infix in self.infixes_to_substitute:
            if infix[0] in question.lower():
                question = re.sub(infix[1], infix[2], question).strip()
                break

        return question

    def _get_num_sentences(self, question):
        parsed = self.parser(question)
        return len([sent for sent in parsed.sents])

    def _get_multi_sent_decomposition(self, question):
        parsed = self.parser(question)
        sents = [sent.text for sent in parsed.sents]

        # extract mention-reference sentence pairs
        replace_pairs = []
        if parsed._.coref_clusters is not None:
            for cluster in parsed._.coref_clusters:
                main_sent = cluster.main.sent.text
                main_sent_index = sents.index(main_sent)
                for mention in cluster.mentions:
                    if mention != cluster.main:
                        mention_sent = mention.sent.text
                        mention_sent_index = sents.index(mention_sent)
                        if main_sent_index != mention_sent_index:
                            replace_pairs.append((mention, main_sent_index))

        # in case there is no coref, treat the text as a single sentence
        if not replace_pairs:
            return []

        # replace any mention with the corresponding reference sentence index
        tokens = [token.text for token in parsed]
        for (mention, ref_sent_index) in replace_pairs:
            remove_indices = [x for x in range(mention.start, mention.end)][::-1]
            for index in remove_indices:
                tokens.pop(index)

            tokens.insert(mention.start, "@@{}@@".format(ref_sent_index+1))

        # parse each sentence separately
        question_coref = self.parser(' '.join(tokens))
        sents_coref = [sent.text for sent in question_coref.sents]

        return [self._parse(self._clean(sent)) for sent in sents_coref]

    def _update_decomposition(self, decomposition, i, decomposed):
        # remove non-decomposed part
        decomposition_previous_len = len(decomposition)
        decomposition.remove(decomposition[i])

        # fix references in text following the decomposed part, by increasing it by len(decomposed) - 1.
        # this way, if the reference was to the i'th position (which is now decomposed), it will be updated
        # to the last part of the decomposition.
        for j in range(i+1, decomposition_previous_len):
            # -1 because we removed one element
            updated_part = re.sub("@@(\d\d)?@@",
                                  lambda x: "@@" + str(int(x.group(1)) + len(decomposed) - 1) + "@@",
                                  decomposition[j-1].text)
            decomposition[j-1] = self._parse(updated_part)

        # insert decomposed parts one by one
        for part in decomposed[::-1]:
            decomposition.insert(i, self._parse(part))

        return decomposition

    def _decompose(self, question, verbose):
        trace = []

        num_sentences = self._get_num_sentences(question)
        if num_sentences > 1:
            decomposition = self._get_multi_sent_decomposition(question)
            if not decomposition:
                decomposition = [self._parse(self._clean(question))]
            else:
                trace.append("multi_sent_coref")
        else:
            decomposition = [self._parse(self._clean(question))]
        if verbose:
            print(decomposition)

        while True:
            is_decomposed = False
            for i, part in enumerate(decomposition):
                decomposed = None
                if self.rules["be_root"].check(part, i + 1):
                    decomposed = self.rules["be_root"].decompose()
                    trace.append("be_root")
                elif self.rules["be_auxpass"].check(part, i + 1):
                    decomposed = self.rules["be_auxpass"].decompose()
                    trace.append("be_auxpass")
                elif self.rules["do_subj"].check(part, i + 1):
                    decomposed = self.rules["do_subj"].decompose()
                    trace.append("do_subj")
                elif self.rules["subj_do_have"].check(part, i+1):
                    decomposed = self.rules["subj_do_have"].decompose()
                    trace.append("subj_do_have")
                elif self.rules["conjunction"].check(part, i+1):
                    decomposed = self.rules["conjunction"].decompose()
                    trace.append("conjunction")
                elif self.rules["how_many"].check(part, i+1):
                    decomposed = self.rules["how_many"].decompose()
                    trace.append("how_many")
                elif self.rules["multi_prep"].check(part, i+1):
                    decomposed = self.rules["multi_prep"].decompose()
                    trace.append("multi_prep")
                elif self.rules["single_prep"].check(part, i+1):
                    # check that "relcl" should not be applied
                    single_prep_index = self.rules["single_prep"].prep_index
                    if self.rules["relcl"].check(part, i + 1) and \
                            self.rules["relcl"].check_relcl_contains_index(single_prep_index):
                        decomposed = self.rules["relcl"].decompose()
                        trace.append("relcl")
                    else:
                        decomposed = self.rules["single_prep"].decompose()
                        trace.append("single_prep")
                elif self.rules["relcl"].check(part, i+1):
                    decomposed = self.rules["relcl"].decompose()
                    trace.append("relcl")
                elif self.rules["superlative"].check(part, i+1):
                    decomposed = self.rules["superlative"].decompose()
                    trace.append("superlative")
                elif self.rules["acl_verb"].check(part, i+1):
                    decomposed = self.rules["acl_verb"].decompose()
                    trace.append("acl_verb")

                if decomposed:
                    decomposition = self._update_decomposition(decomposition, i, decomposed)
                    is_decomposed = True
                    if verbose:
                        print(decomposition)

            if not is_decomposed:
                break

        return decomposition, trace
