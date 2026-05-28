class FeedbackTool:
    """
    Evaluates user answers, records performance metrics in memory,
    and leverages the LLM to generate warm, custom explanations and hints.
    """
    def __init__(self, memory_tool=None, llm_provider=None):
        self.memory_tool = memory_tool
        self.llm_provider = llm_provider

    def set_llm_provider(self, provider):
        """Allows dynamic updates of LLM provider configs."""
        self.llm_provider = provider

    def check_answer(self, scenario_label, user_answer, correct_answer, target_word, lang="English"):
        """
        Validates the answer. If correct, records success and decays the mistake score.
        If incorrect, records a mistake and provides educational explanations.
        """
        is_correct = user_answer.strip().lower() == correct_answer.strip().lower()
        
        # 1. Update memory
        if self.memory_tool:
            if is_correct:
                self.memory_tool.record_success(scenario_label, target_word)
            else:
                self.memory_tool.record_mistake(scenario_label, target_word, "wrong_vocabulary")

        # 2. Invoke LLM for creative educational feedback or generate standard feedback
        explanation = self._generate_llm_feedback(
            is_correct=is_correct,
            user_ans=user_answer,
            correct_ans=correct_answer,
            target_word=target_word,
            scenario=scenario_label,
            lang=lang
        )

        return is_correct, explanation

    def _generate_llm_feedback(self, is_correct, user_ans, correct_ans, target_word, scenario, lang):
        """
        Generates contextual corrections or encouraging feedback from the LLM.
        """
        system_prompt = (
            "You are a friendly, encouraging Swedish language tutor named Sven. "
            "Explain the feedback clearly and concisely in a beginner-friendly manner. "
            f"Use the user's selected translation language: {lang}.\n"
            "Keep your output short (max 2-3 sentences)."
        )
        
        if is_correct:
            user_prompt = (
                f"The user answered correctly! They chose the word '{correct_ans}' to complete the Swedish sentence. "
                f"Provide a brief, positive validation in Swedish (like 'Bra gjort!' or 'Helt rätt!'), "
                f"explain what the Swedish sentence means in {lang}, and reinforce learning."
            )
        else:
            user_prompt = (
                f"The user answered incorrectly in a Swedish exercise for the scenario '{scenario}'.\n"
                f"They guessed: '{user_ans}'\n"
                f"The correct answer is: '{correct_ans}' (target word: '{target_word}').\n"
                f"Explain why '{correct_ans}' is the correct fit, give a brief and helpful hint "
                f"in {lang} explaining the word's meaning or Swedish usage, and encourage them to try again."
            )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        if self.llm_provider:
            try:
                response = self.llm_provider.chat_complete(messages, temperature=0.6)
                if response and "Error:" not in response:
                    return response
            except Exception as e:
                print(f"Feedback LLM invocation failed: {e}")

        # Fallback standard static responses if LLM offline/error
        if is_correct:
            meaning = f"the correct phrase is indeed '{correct_ans}'."
            return (
                f"🇸🇪 Bra jobbat! (Well done!) You got it right! "
                f"The sentence is complete: '{correct_ans}'. "
                f"This perfectly matches the Swedish dialog scenario."
            )
        else:
            return (
                f"🇸🇪 Oj! (Oops!) That was incorrect. "
                f"The correct answer is '{correct_ans}'. "
                f"Hint: This Swedish word fits the sentence context. Try repeating the sentence: '... {correct_ans}'."
            )
