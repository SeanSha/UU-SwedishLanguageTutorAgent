import random
import re
from tools.scenario_tool import ScenarioTool
from tools.memory_tool import MemoryTool
from tools.vocab_resolver import is_resolved

class QuizTool:
    """
    Constructs multiple-choice or fill-in-the-blank vocabulary quizzes for the student,
    injecting past mistake vocabulary as distracting options to test reinforcement.
    """
    def __init__(self, scenario_tool=None, memory_tool=None):
        self.scenario_tool = scenario_tool or ScenarioTool()
        self.memory_tool = memory_tool or MemoryTool()
        self.structured_vocab = []
        self.scenario_mapping = {}

    def set_structured_dataset(self, vocab_items, scenario_mapping=None):
        """Provides topic vocabulary from the structured dataset for better distractors."""
        self.structured_vocab = vocab_items or []
        self.scenario_mapping = scenario_mapping or {}

    def _structured_words_for_scenario(self, scenario_label):
        scenario_db = self.scenario_mapping.get(scenario_label, scenario_label)
        return [
            item.get("word", "").strip()
            for item in self.structured_vocab
            if item.get("scenario") == scenario_db and item.get("word")
        ]

    def _extract_keywords(self, sentence):
        """Helper to find nouns, verbs, or adjectives to blank out (words > 3 chars)."""
        words = re.findall(r'\b\w+\b', sentence)
        # Filter for interesting content words (exclude short prepositions)
        candidates = [w for w in words if len(w) > 3 and w.lower() not in ["vill", "eller", "inte", "till", "från", "mitt"]]
        if not candidates:
            # Fallback if all words are short
            candidates = words if words else ["svenska"]
        return candidates

    def generate_quiz(self, scenario_label, target_sentence, quiz_type="multiple_choice"):
        """
        Creates a vocabulary quiz by blanking out a keyword from the Swedish sentence.
        Generates related options, optionally injecting user struggle words.
        """
        # 1. Select the word to hide
        keywords = self._extract_keywords(target_sentence)
        known_keywords = [w for w in keywords if is_resolved(w, self.structured_vocab, {})]
        if known_keywords:
            keywords = known_keywords
        correct_word = random.choice(keywords)
        
        # Ensure regex replaces only the specific word exactly as a boundary word
        pattern = re.compile(r'\b' + re.escape(correct_word) + r'\b')
        
        if quiz_type == "multiple_choice":
            blanked_sentence = pattern.sub("____", target_sentence)
        else:
            # Fill in the blank with starting letter, e.g. "äpple" -> "ä____"
            starting_letter = correct_word[0]
            blanked_sentence = pattern.sub(f"{starting_letter}____", target_sentence)

        # 2. Gather distractors
        distractors = set()
        
        # A. Pull user struggle words for this scenario (Reinforcement)
        struggles = self.memory_tool.get_struggle_words(scenario_label)
        for w in struggles:
            w_clean = w.strip()
            if w_clean.lower() != correct_word.lower() and len(w_clean) > 1:
                distractors.add(w_clean)
                if len(distractors) >= 2: # Keep at most 2 struggle distractors
                    break

        # B. Pull structured vocabulary from the same selected topic as backups
        sc_words = self._structured_words_for_scenario(scenario_label)
        random.shuffle(sc_words)
        for w in sc_words:
            w_clean = w.strip()
            if w_clean.lower() != correct_word.lower() and len(w_clean) > 2:
                if w_clean.lower() not in [d.lower() for d in distractors]:
                    distractors.add(w_clean)
            if len(distractors) >= 3:
                break

        # C. Pull general words from same legacy scenario labels as backups
        scenario_sentences = self.scenario_tool.get_sentences_by_scenario(scenario_label)
        legacy_words = []
        for item in scenario_sentences:
            legacy_words.extend(self._extract_keywords(item["text"]))
            
        # Add random words from the scenario that don't match the correct word
        random.shuffle(legacy_words)
        for w in legacy_words:
            w_clean = w.strip()
            if w_clean.lower() != correct_word.lower() and len(w_clean) > 2:
                # Basic string uniqueness check
                if w_clean.lower() not in [d.lower() for d in distractors]:
                    distractors.add(w_clean)
            if len(distractors) >= 3:
                break

        # D. Generic fallbacks if we still don't have 3 distractors
        generics = ["kaffe", "buss", "läkare", "äpple", "skola", "biljett", "lägenhet", "svenska"]
        random.shuffle(generics)
        for w in generics:
            if len(distractors) >= 3:
                break
            if w.lower() != correct_word.lower() and w.lower() not in [d.lower() for d in distractors]:
                distractors.add(w)

        # 3. Compile and shuffle options
        options = list(distractors)[:3] + [correct_word]
        # Preserve capitalization of the target word in option list
        options = list(set(options)) # unique check
        
        # Make sure we have exactly 4 options
        while len(options) < 4:
            fallback = random.choice(generics)
            if fallback not in options:
                options.append(fallback)
        options = options[:4]
        
        random.shuffle(options)

        return {
            "sentence_with_blank": blanked_sentence,
            "correct_answer": correct_word,
            "options": options,
            "quiz_type": quiz_type,
            "target_word": correct_word
        }

if __name__ == "__main__":
    from tools.scenario_tool import ScenarioTool
    from tools.memory_tool import MemoryTool
    
    st = ScenarioTool()
    mt = MemoryTool()
    mt.record_mistake("food_shop", "kaffe")

    qt = QuizTool(scenario_tool=st, memory_tool=mt)
    quiz = qt.generate_quiz("food_shop", "En kopp kaffe, tack.", quiz_type="multiple_choice")
    print("Quiz:", quiz)
