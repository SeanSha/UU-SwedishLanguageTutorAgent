"""
Unified retrieval over structured Pre-A1 datasets (dialogue plans, sentences,
vocabulary, function schema) for a UI topic tag. Produces one LLM context bundle
and a UI-compatible retrieval log.
"""
import re
from typing import Any, Callable, Dict, List, Optional


class StructuredRetrievalTool:
    def __init__(
        self,
        vocab_items: List[dict],
        sentence_examples: List[dict],
        dialogue_plans: List[dict],
        function_schema: Dict[str, str],
        memory_tool=None,
        scenario_mapping: Optional[Dict[str, str]] = None,
    ):
        self.vocab_items = vocab_items or []
        self.sentence_examples = sentence_examples or []
        self.dialogue_plans = dialogue_plans or []
        self.function_schema = function_schema or {}
        self.memory_tool = memory_tool
        self.scenario_mapping = scenario_mapping or {}

    def resolve_db_scenario(self, scenario_label: str) -> str:
        """Maps UI topic tag (e.g. food_shop) to dataset scenario id (e.g. matbutik)."""
        if scenario_label in self.scenario_mapping:
            return self.scenario_mapping[scenario_label]
        reverse = {v: k for k, v in self.scenario_mapping.items()}
        if scenario_label in reverse:
            return scenario_label
        return scenario_label

    @staticmethod
    def _tokenize(text: str) -> set:
        return set(re.findall(r"\b\w+\b", (text or "").lower()))

    def _overlap_score(self, query: str, *texts: str) -> float:
        q = self._tokenize(query)
        if not q:
            return 0.0
        corpus = self._tokenize(" ".join(texts))
        if not corpus:
            return 0.0
        return len(q & corpus) / len(q)

    def _memory_boost(self, scenario_label: str, text: str) -> float:
        if not self.memory_tool:
            return 0.0
        text_lower = text.lower()
        sc_mem = self.memory_tool.memory_data.get(scenario_label, {})
        wrong_words = sc_mem.get("wrong_words", {})
        boost = 0.0
        for word, weight in wrong_words.items():
            if word in text_lower:
                boost += 0.15 * weight
        return boost

    def _filter_vocab(self, scenario_db: str) -> List[dict]:
        return [v for v in self.vocab_items if v.get("scenario") == scenario_db]

    def _filter_sentences(self, scenario_db: str) -> List[dict]:
        return [s for s in self.sentence_examples if s.get("scenario") == scenario_db]

    def _filter_plans(self, scenario_db: str) -> List[dict]:
        return [p for p in self.dialogue_plans if p.get("scenario") == scenario_db]

    def _rank_sentences(
        self, sentences: List[dict], user_query: str, ui_scenario_label: str, top_k: int = 12
    ) -> List[dict]:
        scored = []
        for item in sentences:
            text = item.get("sentence", "")
            base = self._overlap_score(
                user_query,
                text,
                item.get("english", ""),
                item.get("function", ""),
                " ".join(item.get("keywords", []) or []),
            )
            boost = self._memory_boost(ui_scenario_label, text)
            scored.append((base + boost, base, boost, item))
        scored.sort(key=lambda x: x[0], reverse=True)
        out = []
        for final, base, boost, item in scored[:top_k]:
            row = dict(item)
            row["base_score"] = float(base)
            row["boost"] = float(boost)
            row["final_score"] = float(final)
            out.append(row)
        return out

    def _schema_for_functions(self, functions: List[str]) -> Dict[str, str]:
        out = {}
        for fn in functions:
            if fn in self.function_schema:
                out[fn] = self.function_schema[fn]
        return out

    def build_topic_context(
        self,
        scenario_label: str,
        user_query: str,
        plan: Optional[dict],
        retrieved_sequence: List[dict],
    ) -> Dict[str, Any]:
        scenario_db = self.resolve_db_scenario(scenario_label)
        topic_plans = self._filter_plans(scenario_db)
        topic_vocab = self._filter_vocab(scenario_db)
        topic_sentences = self._filter_sentences(scenario_db)
        ranked_sentences = self._rank_sentences(
            topic_sentences, user_query, scenario_label, top_k=12
        )

        functions_in_plan = []
        if plan:
            for step in plan.get("sequence", []):
                fn = step.get("function")
                if fn and fn not in functions_in_plan:
                    functions_in_plan.append(fn)
        for step in retrieved_sequence:
            fn = step.get("function")
            if fn and fn not in functions_in_plan:
                functions_in_plan.append(fn)

        schema_subset = self._schema_for_functions(functions_in_plan)

        ctx = {
            "scenario_label": scenario_label,
            "scenario_db": scenario_db,
            "user_query": user_query,
            "plan": plan,
            "alternate_plans": [
                {"id": p.get("id"), "title": p.get("title"), "micro_goal": p.get("micro_goal")}
                for p in topic_plans
                if plan is None or p.get("id") != plan.get("id")
            ],
            "vocabulary": topic_vocab,
            "ranked_sentences": ranked_sentences,
            "retrieved_sequence": retrieved_sequence,
            "function_schema_subset": schema_subset,
        }
        ctx["llm_context"] = self.format_llm_context(ctx)
        return ctx

    def format_llm_context(self, ctx: Dict[str, Any]) -> str:
        """Single background document for dialogue-generation LLM calls."""
        parts = [
            f"TOPIC TAG (UI): {ctx['scenario_label']}",
            f"DATASET SCENARIO ID: {ctx['scenario_db']}",
            f"LEARNER SITUATION / QUERY: {ctx.get('user_query') or '(general practice)'}",
            "",
        ]

        plan = ctx.get("plan")
        if plan:
            parts.append("=== SELECTED DIALOGUE PLAN ===")
            parts.append(f"ID: {plan.get('id')}")
            parts.append(f"Title: {plan.get('title')}")
            parts.append(f"Micro-goal: {plan.get('micro_goal')}")
            parts.append(f"Description: {plan.get('description')}")
            parts.append("Turn sequence (follow this structure):")
            for step in plan.get("sequence", []):
                parts.append(
                    f"  Turn {step.get('turn')}: speaker={step.get('speaker')}, "
                    f"function={step.get('function')}, goal={step.get('content_goal')}, "
                    f"slots={step.get('required_slots', {})}"
                )
            parts.append("")
        elif ctx.get("alternate_plans"):
            parts.append("=== DIALOGUE PLANS (no single plan selected; pick best fit) ===")
            for p in ctx["alternate_plans"][:6]:
                parts.append(f"- {p.get('title')} ({p.get('micro_goal')})")
            parts.append("")

        if ctx.get("function_schema_subset"):
            parts.append("=== DIALOGUE FUNCTIONS (schema) ===")
            for fn, desc in ctx["function_schema_subset"].items():
                parts.append(f"- {fn}: {desc}")
            parts.append("")

        vocab = ctx.get("vocabulary") or []
        if vocab:
            parts.append(f"=== TOPIC VOCABULARY ({len(vocab)} words) ===")
            for v in vocab[:40]:
                parts.append(
                    f"- {v.get('word')}: {v.get('english')} / {v.get('chinese')} "
                    f"({v.get('part_of_speech', '')}) "
                    f"e.g. {v.get('example_sentence', '')}"
                )
            if len(vocab) > 40:
                parts.append(f"  ... and {len(vocab) - 40} more words")
            parts.append("")

        ranked = ctx.get("ranked_sentences") or []
        if ranked:
            parts.append("=== SCENARIO SENTENCE BANK (ranked for this query) ===")
            for s in ranked:
                parts.append(
                    f"- [{s.get('function')}] {s.get('sentence')} "
                    f"(EN: {s.get('english')}, ZH: {s.get('chinese', '')})"
                )
            parts.append("")

        seq = ctx.get("retrieved_sequence") or []
        if seq:
            parts.append("=== TURN-BY-TURN RETRIEVED EXAMPLES (use these first) ===")
            for step in seq:
                parts.append(
                    f"Turn {step.get('turn')} ({step.get('speaker')}, {step.get('function')}): "
                    f"{step.get('content_goal')} | source: {step.get('source')}"
                )
                for ex in step.get("retrieved_examples") or []:
                    parts.append(
                        f"    → {ex.get('sentence')} (EN: {ex.get('english')}, ZH: {ex.get('chinese', '')})"
                    )
                if not step.get("retrieved_examples"):
                    parts.append("    → (no exact match — stay within vocabulary bank above)")
            parts.append("")

        return "\n".join(parts)

    def to_ui_log(self, ctx: Dict[str, Any], top_k: int = 8) -> List[dict]:
        """Format for Study Guide + IR debug table (text, english, chinese, scores)."""
        seen = set()
        results: List[dict] = []

        for step in ctx.get("retrieved_sequence") or []:
            for ex in step.get("retrieved_examples") or []:
                text = ex.get("sentence", "")
                if not text or text in seen:
                    continue
                seen.add(text)
                results.append(
                    {
                        "text": text,
                        "english": ex.get("english", ""),
                        "chinese": ex.get("chinese", ""),
                        "base_score": 1.0,
                        "boost": 0.0,
                        "final_score": 1.0,
                        "source": f"plan_turn_{step.get('turn')}",
                    }
                )

        for item in ctx.get("ranked_sentences") or []:
            text = item.get("sentence", "")
            if not text or text in seen:
                continue
            seen.add(text)
            results.append(
                {
                    "text": text,
                    "english": item.get("english", ""),
                    "chinese": item.get("chinese", ""),
                    "base_score": item.get("base_score", 0.0),
                    "boost": item.get("boost", 0.0),
                    "final_score": item.get("final_score", 0.0),
                    "source": f"sentence_bank:{item.get('function', '')}",
                }
            )

        return results[:top_k]

    def retrieve_topic_context(
        self,
        scenario_label: str,
        user_query: str,
        plan_selector: Callable[[str, str], Optional[dict]],
        sequence_builder: Callable[[dict], List[dict]],
    ) -> Dict[str, Any]:
        """
        Full pipeline: map topic → select plan → per-turn sentence retrieval →
        vocabulary + schema + ranked corpus → LLM context string.
        """
        scenario_db = self.resolve_db_scenario(scenario_label)
        plan = plan_selector(user_query, scenario_db) if self.dialogue_plans else None
        retrieved_sequence = sequence_builder(plan) if plan else []
        return self.build_topic_context(
            scenario_label, user_query, plan, retrieved_sequence
        )
