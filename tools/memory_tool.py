import os
import json
import config

class MemoryTool:
    """
    Manages user practice mistakes, vocabulary tracking, and CEFR level progress.
    Saves state in memory/user_memory.json.
    """
    def __init__(self):
        self.memory_path = config.USER_MEMORY_PATH
        self.memory_data = {}
        self.load_memory()

    def _initialize_empty_scenario(self):
        return {
            "wrong_words": {},         # word: mistake_score (decayable)
            "mistake_types": {
                "wrong_vocabulary": 0,
                "repeated_wrong_word": 0
            },
            "mistake_count": 0,
            "correct_count": 0
        }

    def load_memory(self):
        """Loads user memory data from JSON file or initializes a new structured store."""
        if os.path.exists(self.memory_path):
            try:
                with open(self.memory_path, 'r', encoding='utf-8') as f:
                    self.memory_data = json.load(f)
            except Exception as e:
                print(f"Error loading user memory JSON: {e}. Resetting memory...")
                self.memory_data = {}
        else:
            self.memory_data = {}

        # Ensure all registered scenarios are represented in the structure
        for scenario in config.SCENARIOS:
            if scenario not in self.memory_data:
                self.memory_data[scenario] = self._initialize_empty_scenario()

    def save_memory(self):
        """Saves current memory state to the JSON file."""
        os.makedirs(os.path.dirname(self.memory_path), exist_ok=True)
        try:
            with open(self.memory_path, 'w', encoding='utf-8') as f:
                json.dump(self.memory_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving user memory JSON: {e}")

    def record_mistake(self, scenario_label, word, mistake_type="wrong_vocabulary"):
        """
        Increments mistake score for a given word and category under a scenario.
        """
        if scenario_label not in self.memory_data:
            self.memory_data[scenario_label] = self._initialize_empty_scenario()

        sc_mem = self.memory_data[scenario_label]
        sc_mem["mistake_count"] += 1

        # Track specific word mistakes (cap at 5 to prevent infinite scaling)
        word_clean = word.strip().lower()
        current_score = sc_mem["wrong_words"].get(word_clean, 0)
        
        if current_score >= 1:
            sc_mem["mistake_types"]["repeated_wrong_word"] = sc_mem["mistake_types"].get("repeated_wrong_word", 0) + 1
        
        sc_mem["wrong_words"][word_clean] = min(current_score + 2, 6) # Boost by 2 for high visibility, max 6
        sc_mem["mistake_types"][mistake_type] = sc_mem["mistake_types"].get(mistake_type, 0) + 1
        
        self.save_memory()

    def record_success(self, scenario_label, word):
        """
        Records a successful answer. Decrements mistake score (decay) for the word.
        """
        if scenario_label not in self.memory_data:
            self.memory_data[scenario_label] = self._initialize_empty_scenario()

        sc_mem = self.memory_data[scenario_label]
        sc_mem["correct_count"] += 1

        word_clean = word.strip().lower()
        if word_clean in sc_mem["wrong_words"]:
            current_score = sc_mem["wrong_words"][word_clean]
            # Reduce score (Spaced Repetition decay)
            new_score = current_score - 1
            if new_score <= 0:
                del sc_mem["wrong_words"][word_clean]
            else:
                sc_mem["wrong_words"][word_clean] = new_score

        self.save_memory()

    def get_struggle_words(self, scenario_label):
        """
        Returns a list of words with positive mistake scores, ordered by score descending.
        """
        if scenario_label not in self.memory_data:
            return []
        
        wrong_words_dict = self.memory_data[scenario_label].get("wrong_words", {})
        # Sort by mistake weight descending
        sorted_words = sorted(wrong_words_dict.items(), key=lambda x: x[1], reverse=True)
        return [word for word, score in sorted_words if score > 0]

    def get_summary(self):
        """
        Returns basic statistics for debug/visual dashboard.
        """
        summary = {}
        for sc in config.SCENARIOS:
            sc_mem = self.memory_data.get(sc, self._initialize_empty_scenario())
            summary[sc] = {
                "mistakes": sc_mem["mistake_count"],
                "successes": sc_mem["correct_count"],
                "active_struggles": list(sc_mem["wrong_words"].keys()),
                "metrics": f"Accuracy: {self._calc_acc(sc_mem)}%"
            }
        return summary

    def _calc_acc(self, sc_mem):
        tot = sc_mem["mistake_count"] + sc_mem["correct_count"]
        if tot == 0:
            return 100
        return round((sc_mem["correct_count"] / tot) * 100, 1)

if __name__ == "__main__":
    mem = MemoryTool()
    mem.record_mistake("food_shop", "äpple")
    mem.record_mistake("food_shop", "äpple")
    mem.record_mistake("food_shop", "kaffe")
    mem.record_success("food_shop", "kaffe")
    print(mem.get_summary()["food_shop"])
