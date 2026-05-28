import os
from agent import SwedishSpeakingAgent, SCENARIO_MAPPING

TEST_CASES = [
    {
        "name": "1. Transport",
        "input": "Bussen har åkt. Jag vill åka till stan.",
        "scenario_label": "transport"
    },
    {
        "name": "2. Matbutik",
        "input": "Jag vill köpa mjölk och bröd.",
        "scenario_label": "food_shop"
    },
    {
        "name": "3. Hälsa & Vård",
        "input": "Jag är sjuk och behöver hjälp.",
        "scenario_label": "health_places"
    },
    {
        "name": "4. Familj & Skola",
        "input": "Mitt barn går i skolan.",
        "scenario_label": "family_school"
    },
    {
        "name": "5. Hem & Platser",
        "input": "Var är köket?",
        "scenario_label": "home_places"
    },
    {
        "name": "6. Presentationer",
        "input": "Hej, jag heter Sean.",
        "scenario_label": "social_intro"
    }
]

def run_tests():
    print("================================================================")
    print("🇸🇪 RUNNING SWEDISH LANGUAGE BUDDY DIALOGUE PLANNER TESTS 🇸🇪")
    print("================================================================")
    
    agent = SwedishSpeakingAgent()
    # Initialize LLM Provider in Local Mode by default (runs qwen2.5 local Ollama)
    print("Initializing LLM provider diagnostics...")
    ok, msg = agent.initialize_provider("Local Mode")
    print(f"LLM Connection status: {msg}\n")
    
    for case in TEST_CASES:
        print(f"\n----------------------------------------------------------------")
        print(f"CASE: {case['name']}")
        print(f"INPUT: '{case['input']}'")
        print(f"----------------------------------------------------------------")
        
        # Scenario Classification Mapping (Task 2)
        scenario_label = case["scenario_label"]
        db_scenario_id = SCENARIO_MAPPING.get(scenario_label, scenario_label)
        print(f"- Detected Scenario Label: {scenario_label}")
        print(f"- Normalized Database Scenario ID: {db_scenario_id}")
        
        # Unified topic retrieval (plans + sentences + vocab + schema)
        topic_context = agent.retrieve_topic_context(scenario_label, case["input"])
        if not topic_context or not topic_context.get("plan"):
            print("🔴 Failed to build topic context / select a plan!")
            continue

        plan = topic_context["plan"]
        print(f"- Selected micro_goal: {plan['micro_goal']}")
        print(f"- Selected plan title: {plan['title']}")
        print(f"- Vocab in context: {len(topic_context.get('vocabulary') or [])}")
        print(f"- Ranked sentences: {len(topic_context.get('ranked_sentences') or [])}")
        print(f"- LLM context length: {len(topic_context.get('llm_context') or '')} chars")

        retrieved_sequence = topic_context.get("retrieved_sequence") or []
        retrieved_funcs = [step["function"] for step in retrieved_sequence]
        print(f"- Retrieved dialogue sequence functions: {', '.join(retrieved_funcs)}")
        
        # Print a retrieved example mapping details
        print("\n[Technical Function-level Sentence Retrieval Details]")
        for idx, step in enumerate(retrieved_sequence[:2]):
            print(f"  Turn {step['turn']} ({step['speaker']} - {step['function']}):")
            print(f"    Content Goal: '{step['content_goal']}'")
            print(f"    Source: {step['source']}")
            if step["retrieved_examples"]:
                print(f"    Example retrieved: '{step['retrieved_examples'][0]['sentence']}' (Eng: {step['retrieved_examples'][0]['english']})")
            else:
                print("    Example retrieved: None (Using generated fallback)")
        if len(retrieved_sequence) > 2:
            print(f"  ... (+ {len(retrieved_sequence) - 2} more turns)")
            
        # Dialogue Planner LLM Generation (Task 5) and Coherence Check (Task 6)
        print("\nInvoking Dialogue Planner and running Coherence Checks...")
        stages = agent.generate_coherent_dialogue(
            scenario_label, case["input"], topic_context=topic_context
        )
        
        if stages:
            print("\n- Final generated dialogue:")
            for idx, stage in enumerate(stages):
                print(f"  Stage {stage['stage']} ({stage['desc']}):")
                print(f"    👨‍🏫 Sven prompt: '{stage['sven_phrase']}' (Eng: {stage.get('sven_english', '')})")
                print(f"    👤 User reply:  '{stage['target_phrase']}' (Eng: {stage.get('target_english', '')})")
            
            # Check coherence outcomes
            is_coherent, issues = agent.check_dialogue_coherence(stages, plan, db_scenario_id)
            if is_coherent:
                print("\n- Coherence check result: 🟢 PASSED contradiction check successfully!")
            else:
                print(f"\n- Coherence check result: 🔴 FAILED! Issues found: {issues}")
        else:
            print("🔴 Failed to generate coherent dialogue via LLM planner (LLM connection offline or parse error).")
            
        print("----------------------------------------------------------------")

if __name__ == "__main__":
    run_tests()
