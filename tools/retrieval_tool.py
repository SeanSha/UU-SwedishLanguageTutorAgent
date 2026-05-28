import os
import re
import numpy as np
from tools.scenario_tool import ScenarioTool
from tools.memory_tool import MemoryTool
import config

class RetrievalTool:
    """
    Retrieval system using semantic vector search (SentenceTransformers)
    or standard keyword similarity (TF-IDF fallback).
    Incorporates memory-aware re-weighting to boost sentences containing difficult words.
    """
    def __init__(self, scenario_tool=None, memory_tool=None):
        self.scenario_tool = scenario_tool or ScenarioTool()
        self.memory_tool = memory_tool or MemoryTool()
        self.model = None
        self._load_vector_model()

    def _load_vector_model(self):
        """Lazy loads SentenceTransformers model. Falls back gracefully to text TF-IDF if unavailable."""
        try:
            from sentence_transformers import SentenceTransformer
            print("Loading paraphrase-multilingual-MiniLM-L12-v2 vector model...")
            self.model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
            print("Vector model loaded successfully!")
        except Exception as e:
            print(f"SentenceTransformers loading failed or not installed: {e}.")
            print("Falling back to standard TF-IDF Keyword Retrieval engine (fully offline/lightweight).")
            self.model = None

    def _fallback_tfidf_similarity(self, query, corpus_texts):
        """
        Lightweight TF-IDF / Jaccard similarity fallback when vector model is missing.
        """
        def tokenize(text):
            return set(re.findall(r'\b\w+\b', text.lower()))

        query_tokens = tokenize(query)
        scores = []
        for text in corpus_texts:
            text_tokens = tokenize(text)
            intersection = query_tokens.intersection(text_tokens)
            union = query_tokens.union(text_tokens)
            score = len(intersection) / len(union) if union else 0.0
            scores.append(score)
        return np.array(scores)

    def retrieve(self, scenario_label, query, top_k=5):
        """
        Filters the dataset by scenario, computes similarity to the query, 
        and applies a memory-aware bias to boost sentences that contain words 
        the user previously got wrong.
        """
        # 1. Fetch scenario sentences
        candidates = self.scenario_tool.get_sentences_by_scenario(scenario_label)
        if not candidates:
            return []

        corpus_texts = [item["text"] for item in candidates]

        # 2. Compute base similarity scores
        if self.model is not None:
            try:
                query_emb = self.model.encode(query, convert_to_tensor=True).cpu().numpy()
                corpus_embs = self.model.encode(corpus_texts, convert_to_tensor=True).cpu().numpy()
                
                # Cosine Similarity
                dot_prod = np.dot(corpus_embs, query_emb)
                norms = np.linalg.norm(corpus_embs, axis=1) * np.linalg.norm(query_emb)
                norms[norms == 0] = 1e-9
                base_scores = dot_prod / norms
            except Exception as e:
                print(f"Vector search failed: {e}. Using fallback similarity.")
                base_scores = self._fallback_tfidf_similarity(query, corpus_texts)
        else:
            base_scores = self._fallback_tfidf_similarity(query, corpus_texts)

        # 3. Memory-Aware Bias Injection (The VG Distinction Feature!)
        # Fetch words user struggled with in this scenario
        struggle_words = self.memory_tool.get_struggle_words(scenario_label)
        
        # Load user memory explicitly to get exact struggle weight scores
        sc_mem = self.memory_tool.memory_data.get(scenario_label, {})
        wrong_words_dict = sc_mem.get("wrong_words", {})

        boosted_scores = base_scores.copy()
        debug_info = []

        for idx, item in enumerate(candidates):
            text_lower = item["text"].lower()
            total_boost = 0.0
            triggered_words = []

            for word in struggle_words:
                # Direct substring match or boundary word check
                if word in text_lower:
                    # Boost magnitude is proportional to the word's struggle score
                    weight = wrong_words_dict.get(word, 0)
                    boost = 0.15 * weight
                    total_boost += boost
                    triggered_words.append(f"{word}(w:{weight}, boost:+{boost:.2f})")

            boosted_scores[idx] += total_boost
            
            # Record debug details for UI debug drawer
            debug_info.append({
                "text": item["text"],
                "base_score": float(base_scores[idx]),
                "boost": float(total_boost),
                "final_score": float(boosted_scores[idx]),
                "triggered_words": triggered_words
            })

        # 4. Sort and return top_k
        sorted_indices = np.argsort(boosted_scores)[::-1]
        
        results = []
        for rank in range(min(top_k, len(sorted_indices))):
            idx = sorted_indices[rank]
            cand = candidates[idx].copy()
            cand["base_score"] = float(base_scores[idx])
            cand["boost"] = debug_info[idx]["boost"]
            cand["final_score"] = float(boosted_scores[idx])
            cand["triggered_words"] = debug_info[idx]["triggered_words"]
            results.append(cand)

        return results

if __name__ == "__main__":
    from tools.scenario_tool import ScenarioTool
    from tools.memory_tool import MemoryTool

    st = ScenarioTool()
    mt = MemoryTool()
    
    # Simulate a mistake
    mt.record_mistake("food_shop", "kaffe")
    mt.record_mistake("food_shop", "kaffe")

    rt = RetrievalTool(scenario_tool=st, memory_tool=mt)
    
    # Query for breakfast
    res = rt.retrieve("food_shop", "frukost kaffe", top_k=3)
    for r in res:
        print(f"Text: {r['text']} | Final Score: {r['final_score']:.2f} (Base: {r['base_score']:.2f}, Boost: {r['boost']:.2f}) | Triggered: {r['triggered_words']}")
