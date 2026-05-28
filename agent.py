import os
import random
import re
import json
from llm.llm_provider import LLMProvider
from tools.scenario_tool import ScenarioTool
from tools.memory_tool import MemoryTool
from tools.retrieval_tool import RetrievalTool
from tools.dialogue_tool import DialogueTool
from tools.quiz_tool import QuizTool
from tools.feedback_tool import FeedbackTool
from tools.tts_avatar_tool import TTSAvatarTool
from tools.structured_retrieval_tool import StructuredRetrievalTool
from tools.vocab_resolver import resolve_vocab
import config

# Rich offline Swedish-English dictionary for instant pre-A1 vocabulary study guide
OFFLINE_DICT = {
    # food_shop
    "äpple": "apple (ett äpple / äpplen) 🍎",
    "äpplen": "apples 🍎",
    "kaffe": "coffee (en kopp kaffe) ☕",
    "bröd": "bread 🍞",
    "påse": "bag (en påse / påsar) 🛍️",
    "mjölk": "milk 🥛",
    "tack": "please / thank you 🙏",
    "kopp": "cup ☕",
    "kostar": "costs 💰",
    "köpa": "to buy 🛒",
    "tomater": "tomatoes 🍅",
    # family_school
    "studerar": "studies / studying 📚",
    "svenska": "Swedish 🇸🇪",
    "penna": "pen ✏️",
    "familj": "family 👨‍👩‍👧‍👦",
    "skola": "school 🏫",
    "lärare": "teacher 🧑‍🏫",
    "bror": "brother 👦",
    "syster": "sister 👧",
    # health_places
    "mår": "feels / feeling (mår bra: feel well) 😊",
    "inte": "not ❌",
    "bra": "good 👍",
    "sjukhus": "hospital 🏥",
    "sjukhuset": "the hospital 🏥",
    "huvudet": "the head (ont i huvudet: headache) 🧠",
    "läkare": "doctor 🩺",
    "medicin": "medicine 💊",
    "ont": "pain / hurt 🤕",
    "sjuk": "sick 🤒",
    "apoteket": "the pharmacy 🏪",
    # transport
    "busshållplatsen": "the bus stop 🚌",
    "tåget": "the train 🚆",
    "biljett": "ticket 🎫",
    "bussen": "the bus 🚌",
    "stan": "town / city center 🏙️",
    "tunnelbanan": "the subway 🚇",
    "stationen": "the station 🚉",
    "snabb": "fast ⚡",
    "ursäkta": "excuse me 🙋",
    # home_places
    "bor": "lives / living 🏠",
    "lägenhet": "apartment 🏢",
    "rum": "room 🔑",
    "köket": "the kitchen 🍳",
    "toaletten": "the toilet 🚽",
    "huset": "the house 🏠",
    "trädgård": "garden 🏡",
    "soffan": "the sofa 🛋️",
    # social_intro
    "hej": "hello 👋",
    "heter": "is named / called (vad heter du: what's your name) 🏷️",
    "trevligt": "nice (trevligt att träffas: nice to meet you) 😊",
    "träffas": "to meet 🤝",
    "varifrån": "where from 🗺️",
    "kommer": "comes / coming 🚶",
    "kina": "China 🇨🇳",
    "talar": "speaks / speaking 🗣️",
    "lite": "little / a bit 🤏",
    "hur": "how ❓",
    "du": "you 👤",
    "jag": "I / me 👤",
    "namn": "name 🏷️"
}

SVEN_TRANSLATIONS = {
    # food_shop
    "Hej! Välkommen till matbutiken. Kan jag hjälpa dig?": {
        "English": "Hello! Welcome to the grocery store. Can I help you?",
        "Chinese": "你好！欢迎来到食品店。有什么可以帮您的？"
    },
    "Vad vill du köpa idag?": {
        "English": "What do you want to buy today?",
        "Chinese": "你今天想买什么？"
    },
    "Här är äpplet. Något mer?": {
        "English": "Here is the apple. Anything else?",
        "Chinese": "这是苹果。还要别的吗？"
    },
    "Det kostar tio kronor. Vill du ha en påse?": {
        "English": "It costs ten kronor. Do you want a bag?",
        "Chinese": "一共十克朗。你需要袋子吗？"
    },
    "Ja, här är påsen. Det blir tio kronor.": {
        "English": "Yes, here is the bag. That will be ten kronor.",
        "Chinese": "好的，这是袋子。一共十克朗。"
    },

    # social_intro
    "Hej! Jag heter Sven. Vad heter du?": {
        "English": "Hello! My name is Sven. What is your name?",
        "Chinese": "你好！我叫 Sven。你叫什么名字？"
    },
    "Trevligt att träffas! Varifrån kommer du?": {
        "English": "Nice to meet you! Where do you come from?",
        "Chinese": "很高兴认识你！你来自哪里？"
    },
    "Vad roligt! Talar du svenska?": {
        "English": "How fun! Do you speak Swedish?",
        "Chinese": "太好了！你会说瑞典语吗？"
    },
    "Ja, du talar jättebra! Hur mår du idag?": {
        "English": "Yes, you speak very well! How are you doing today?",
        "Chinese": "是的，你说得非常好！你今天怎么样？"
    },
    "Jag mår också bra, tack! Vi ses!": {
        "English": "I feel good too, thanks! See you!",
        "Chinese": "我也很好，谢谢！再见！"
    },

    # family_school
    "Hej! Vad gör du på fritiden?": {
        "English": "Hello! What do you do in your free time?",
        "Chinese": "你好！你闲暇时间做什么？"
    },
    "Vad spännande! Skriver du mycket?": {
        "English": "How exciting! Do you write a lot?",
        "Chinese": "真棒！你经常写字/写作吗？"
    },
    "Ja, här är en penna. Bor du med kompisar?": {
        "English": "Yes, here is a pen. Do you live with friends?",
        "Chinese": "是的，这里有一支笔。你和朋友们住在一起吗？"
    },
    "Vilken fin familj! Går du i skolan?": {
        "English": "What a nice family! Do you go to school?",
        "Chinese": "多么美好的家庭！你上学吗？"
    },
    "Min lärare heter Maria. Har du syskon?": {
        "English": "My teacher is named Maria. Do you have siblings?",
        "Chinese": "我的老师名叫 Maria。你有兄弟姐妹吗？"
    },

    # health_places
    "Hej! Hur mår du idag?": {
        "English": "Hello! How are you feeling today?",
        "Chinese": "你好！你今天感觉怎么样？"
    },
    "Vad tråkigt att höra. Var har du ont?": {
        "English": "So sorry to hear that. Where does it hurt?",
        "Chinese": "听到这个消息真遗憾。你哪里疼？"
    },
    "Du kanske behöver åka till sjukhuset.": {
        "English": "Maybe you need to go to the hospital.",
        "Chinese": "你可能需要去医院。"
    },
    "Det ligger nära stationen. Vill du träffa en läkare?": {
        "English": "It lies near the station. Do you want to see a doctor?",
        "Chinese": "它就在车站附近。你想看医生吗？"
    },
    "Okej, jag ringer en läkare nu. Krya på dig!": {
        "English": "Okay, I am calling a doctor now. Get well soon!",
        "Chinese": "好的，我现在给医生打电话。祝你早日康复！"
    },

    # transport
    "Ursäkta, bussen har åkt.": {
        "English": "Excuse me, the bus has departed.",
        "Chinese": "打扰一下，公交车已经开走了。"
    },
    "Den är runt hörnet. Ska du åka långt?": {
        "English": "It is around the corner. Are you traveling far?",
        "Chinese": "它就在拐角处。你要去很远的地方吗？"
    },
    "Du kan köpa den på bussen. Vart ska du åka?": {
        "English": "You can buy it on the bus. Where are you going?",
        "Chinese": "你可以在公交车上买票。你要去哪里？"
    },
    "Ja, men tåget är snabbare.": {
        "English": "Yes, but the train is faster.",
        "Chinese": "是的，但是火车更快。"
    },
    "Ja, tunnelbanan är mycket snabb. Stationen är nära.": {
        "English": "Yes, the subway is very fast. The station is near.",
        "Chinese": "是的，地铁非常快。车站就在附近。"
    },

    # home_places
    "Hej! Välkommen hem till mig. Var bor du?": {
        "English": "Hello! Welcome to my home. Where do you live?",
        "Chinese": "你好！欢迎来到我家。你住哪里？"
    },
    "Vad trevligt! Kom in, så visar jag huset.": {
        "English": "How nice! Come in, I will show you the house.",
        "Chinese": "真好！进来吧，我带你看看这栋房子。"
    },
    "Fint rum! Här är köket.": {
        "English": "Nice room! Here is the kitchen.",
        "Chinese": "很棒的房间！这里是厨房。"
    },
    "Ja, men det fungerar bra. Behöver du tvätta händerna?": {
        "English": "Yes, but it works well. Do you need to wash your hands?",
        "Chinese": "是的，但它很好用。你需要洗手吗？"
    },
    "Den är till vänster. Kolla, vi har en stor trädgård.": {
        "English": "It is to the left. Look, we have a big garden.",
        "Chinese": "它在左边。看，我们有一个大花园。"
    }
}

SCENARIO_MAPPING = {
    "food_shop": "matbutik",
    "family_school": "familj_skola",
    "health_places": "halsa_vard",
    "transport": "transport",
    "home_places": "hem_platser",
    "social_intro": "presentationer"
}

class SwedishSpeakingAgent:
    """
    Central Agent orchestrator. Incorporates conversation context history,
    Memory-Biased RAG IR, edge-tts/gTTS, and consistent Sven avatar drawings.
    Exposes instant offline vocabulary lookups to eliminate 30-second completion latencies.
    Updates the dialogue generation mechanism to follow a structured dialogue planner.
    """
    def __init__(self):
        self.scenario_tool = ScenarioTool()
        self.memory_tool = MemoryTool()
        self.retrieval_tool = RetrievalTool(self.scenario_tool, self.memory_tool)
        self.dialogue_tool = DialogueTool()
        self.quiz_tool = QuizTool(self.scenario_tool, self.memory_tool)
        
        self.llm_provider = None
        self.llm_available = False
        self.feedback_tool = FeedbackTool(self.memory_tool)
        self.tts_avatar_tool = TTSAvatarTool()

        # Session states
        self.current_scenario = None
        self.active_turn_data = None
        self.active_quiz = None
        self.chat_history = []  # List of {"role": "user"/"assistant", "content": "..."}
        self.thought_logs = []
        self.retrieved_examples_log = []
        self.current_vocab_hints = ""  # Definitions of words in current options
        self.current_translation = ""  # Swedish-English/Chinese translation of current turn
        self.selected_plan_info = ""   # Selected plan details to show in visual status label
        self.topic_context = None      # Unified retrieval bundle for active topic

        # Structured HF dataset loading
        try:
            from data_loader import load_structured_dataset
            self.vocab_items, self.sentence_examples, self.dialogue_plans, self.function_schema = load_structured_dataset()
            self._update_offline_dict_from_hf()
        except Exception as e:
            print(f"Error loading structured dataset: {e}")
            self.vocab_items = []
            self.sentence_examples = []
            self.dialogue_plans = []
            self.function_schema = {}

        self.quiz_tool.set_structured_dataset(self.vocab_items, SCENARIO_MAPPING)

        self.structured_retrieval = StructuredRetrievalTool(
            self.vocab_items,
            self.sentence_examples,
            self.dialogue_plans,
            self.function_schema,
            memory_tool=self.memory_tool,
            scenario_mapping=SCENARIO_MAPPING,
        )

    def _update_offline_dict_from_hf(self):
        """Automatically populates OFFLINE_DICT using vocabulary split items from the Hugging Face dataset."""
        if not hasattr(self, "vocab_items") or not self.vocab_items:
            return
        print(f"Dynamically loading {len(self.vocab_items)} vocabulary items from Hugging Face dataset into offline cache...")
        for item in self.vocab_items:
            word = item.get("word", "").strip().lower()
            eng = item.get("english", "")
            chn = item.get("chinese", "")
            pos = item.get("part_of_speech", "")
            notes = item.get("notes", "")
            if word:
                desc = f"{eng} ({pos})"
                if notes:
                    desc += f" {notes}"
                # Keep emojis from old OFFLINE_DICT if present
                old_desc = OFFLINE_DICT.get(word, "")
                emoji = ""
                if old_desc:
                    # extract emoji at the end
                    import re
                    emojis = re.findall(r'[\U00010000-\U0010ffff\u2600-\u27ff]', old_desc)
                    if emojis:
                        emoji = " " + emojis[-1]
                OFFLINE_DICT[word] = desc + emoji

    def select_dialogue_plan(self, user_input, scenario_id):
        """
        Filters dialogue_plans by scenario_id and selects the best matching plan.
        Filters by:
        1. Exact micro_goal match using keywords.
        2. Keyword overlap scoring.
        3. Falls back to first plan for that scenario if no high score plan is found.
        """
        mapped_scenario = SCENARIO_MAPPING.get(scenario_id, scenario_id)
        
        plans = [p for p in self.dialogue_plans if p.get("scenario") == mapped_scenario]
        if not plans:
            print(f"No dialogue plans found in database split for scenario: '{mapped_scenario}'")
            return None
            
        print(f"Found {len(plans)} plans for scenario: '{mapped_scenario}'")
        
        user_input_lower = user_input.lower()
        
        best_plan = None
        best_score = -1
        
        for plan in plans:
            score = 0
            plan_text = " ".join([
                plan.get("micro_goal", ""),
                plan.get("title", ""),
                plan.get("description", "")
            ]).lower()
            
            seq_texts = []
            for step in plan.get("sequence", []):
                seq_texts.append(step.get("content_goal", ""))
                seq_texts.append(step.get("function", ""))
            plan_text += " " + " ".join(seq_texts).lower()
            
            tokens = set(re.findall(r'\b\w+\b', plan_text))
            query_tokens = set(re.findall(r'\b\w+\b', user_input_lower))
            
            overlap = query_tokens.intersection(tokens)
            score = len(overlap)
            
            micro_goal = plan.get("micro_goal", "").lower()
            if micro_goal in user_input_lower or micro_goal.replace("_", " ") in user_input_lower:
                score += 5
                
            if "bussen" in user_input_lower and micro_goal == "missed_bus_find_alternative":
                score += 10
            if "mjölk" in user_input_lower and micro_goal == "buy_basic_food":
                score += 10
            if "sjuk" in user_input_lower and micro_goal == "ask_for_help_when_sick":
                score += 10
            if "barn" in user_input_lower and micro_goal == "ask_about_child_school":
                score += 10
            if "köket" in user_input_lower and micro_goal == "ask_where_room_is":
                score += 10
            if "sean" in user_input_lower and micro_goal == "introduce_name":
                score += 10
                
            if score > best_score:
                best_score = score
                best_plan = plan
                
        if best_plan:
            print(f"Selected Dialogue Plan: '{best_plan['title']}' (micro_goal: '{best_plan['micro_goal']}') with matching score {best_score}")
        else:
            best_plan = plans[0]
            print(f"Fallback to default dialogue plan: '{best_plan['title']}'")
            
        return best_plan

    def _score_sentence_for_plan_step(self, sentence_item, step):
        """
        Rank sentence examples by the actual dialogue-plan step, especially
        function and required slot values. This keeps retrieved examples tied
        to the selected topic instead of drifting to a random same-function line.
        """
        func = step.get("function", "")
        goal = step.get("content_goal", "")
        slots = step.get("required_slots", {}) or {}
        sentence_blob = " ".join(
            [
                sentence_item.get("sentence", ""),
                sentence_item.get("english", ""),
                sentence_item.get("chinese", ""),
                sentence_item.get("function", ""),
                " ".join(sentence_item.get("keywords", []) or []),
                " ".join(str(v) for v in (sentence_item.get("slots", {}) or {}).values()),
            ]
        ).lower()

        score = 0.0
        if sentence_item.get("function") == func:
            score += 6.0

        for value in slots.values():
            for token in re.findall(r"\b\w+\b", str(value).lower()):
                if token and token in sentence_blob:
                    score += 3.0

        for token in re.findall(r"\b\w+\b", f"{goal} {func}".lower()):
            if len(token) > 2 and token in sentence_blob:
                score += 0.5

        return score

    def _fallback_sentence_for_step(self, step):
        """
        Creates a tiny pre-A1 fallback only when retrieval misses. These are
        intentionally simple and slot-aware so the dialogue still follows the plan.
        """
        func = step.get("function", "")
        speaker = step.get("speaker", "")
        slots = step.get("required_slots", {}) or {}
        place = slots.get("place", "")
        item = slots.get("item", place or "det")
        person = slots.get("person", item)
        if person == "barn" or "child" in (step.get("content_goal", "") or "").lower():
            person = "barnet"
        problem = slots.get("problem", "")
        symptom = slots.get("symptom", "")
        event = slots.get("event", "")
        destination = slots.get("destination", "")
        transport = slots.get("transport", "bussen")
        option = slots.get("option", "")
        quantity = slots.get("quantity", "ett")
        price = slots.get("price", "trettio kronor")
        action = slots.get("action", "det")
        location = slots.get("location", "här")
        direction = slots.get("direction", "till höger")
        name = slots.get("name", "Lina")

        if func == "state_problem" and problem:
            if problem.startswith("mår"):
                problem_sv = f"Jag {problem}."
                problem_en = "I do not feel well." if "inte bra" in problem else f"I {problem}."
                problem_zh = "我感觉不舒服。" if "inte bra" in problem else problem
            elif problem.startswith("missade"):
                problem_sv = f"Jag {problem}."
                problem_en = "I missed the bus." if "bussen" in problem else f"I {problem}."
                problem_zh = "我错过了公交车。" if "bussen" in problem else problem
            elif "bussen" in problem and ("borta" in problem or "åkt" in problem):
                problem_sv = "Bussen har åkt."
                problem_en = "The bus has left."
                problem_zh = "公交车已经走了。"
            else:
                problem_sv = problem.capitalize() + "."
                problem_en = problem
                problem_zh = problem
        else:
            problem_sv = "Jag har ett problem."
            problem_en = "I have a problem."
            problem_zh = "我有一个问题。"

        person_en = "the child" if person == "barnet" else person
        person_zh = "孩子" if person == "barnet" else person
        location_en = "school" if location == "skolan" else location
        location_zh = "学校" if location == "skolan" else location
        is_pickup_time = "pickup" in (step.get("content_goal", "") or "").lower()
        time_value = slots.get("time", "klockan nio")
        time_en = "at three o'clock" if time_value == "klockan tre" else time_value

        templates = {
            "greeting": ("Hej!", "Hello!", "你好！"),
            "offer_help": ("Kan jag hjälpa dig?", "Can I help you?", "我可以帮你吗？"),
            "state_want": (f"Jag vill ha {item}.", f"I want {item}.", f"我想要{item}。"),
            "state_need": (f"Jag behöver {item}.", f"I need {item}.", f"我需要{item}。"),
            "ask_item": (f"Har ni {item}?", f"Do you have {item}?", f"你们有{item}吗？"),
            "ask_quantity": (f"Hur många {item}?", f"How many {item}?", f"多少{item}？"),
            "state_quantity": (f"{quantity} {item}, tack.", f"{quantity} {item}, please.", f"{quantity}{item}，谢谢。"),
            "ask_price": ("Vad kostar det?", "How much does it cost?", "多少钱？"),
            "state_price": (f"Det kostar {price}.", f"It costs {price}.", f"价格是{price}。"),
            "ask_permission": (f"Kan jag {action}?", f"Can I {action}?", f"我可以{action}吗？"),
            "confirm_yes": ("Ja, det går bra.", "Yes, that is fine.", "可以，没问题。"),
            "confirm_no": ("Nej, tyvärr.", "No, unfortunately.", "不，很抱歉。"),
            "ask_location": (f"Var är {person}?", f"Where is {person_en}?", f"{person_zh}在哪里？"),
            "give_location": (f"{person.capitalize()} är i {location}.", f"{person_en.capitalize()} is at {location_en}.", f"{person_zh}在{location_zh}。"),
            "give_direction": (f"Gå {direction}.", f"Go {direction}.", f"往{direction}走。"),
            "state_problem": (problem_sv, problem_en, problem_zh),
            "ask_help": ("Kan du hjälpa mig?", "Can you help me?", "你能帮我吗？"),
            "ask_name": ("Vad heter du?", "What is your name?", "你叫什么名字？"),
            "state_name": (f"Jag heter {name}.", f"My name is {name}.", f"我叫{name}。"),
            "ask_origin": ("Varifrån kommer du?", "Where are you from?", "你来自哪里？"),
            "state_origin": ("Jag kommer från Kina.", "I come from China.", "我来自中国。"),
            "ask_language": ("Talar du svenska?", "Do you speak Swedish?", "你会说瑞典语吗？"),
            "state_language": ("Jag talar lite svenska.", "I speak a little Swedish.", "我会说一点瑞典语。"),
            "ask_symptom": ("Var har du ont?", "Where does it hurt?", "你哪里疼？"),
            "state_symptom": (f"Jag har {symptom}." if symptom else "Jag har ont i huvudet.", f"I have {symptom}." if symptom else "I have a headache.", f"我有{symptom}。" if symptom else "我头疼。"),
            "ask_time": ("När kan jag hämta barnet?" if "hämta" in event else (f"När kommer {event}?" if event else "När går bussen?"), "When can I pick up the child?" if "hämta" in event else (f"When does {event} come?" if event else "When does the bus leave?"), "我什么时候可以接孩子？" if "hämta" in event else (f"{event}什么时候来？" if event else "公交车什么时候走？")),
            "state_time": (f"Du kan hämta barnet {time_value}." if is_pickup_time or "hämta" in event else (f"Den kommer {time_value}." if time_value == "snart" else f"Den går {time_value}."), f"You can pick up the child {time_en}." if is_pickup_time or "hämta" in event else (f"It comes {time_en}." if time_value == "snart" else f"It leaves {time_en}."), f"你可以{time_value}接孩子。" if is_pickup_time or "hämta" in event else f"它{time_value}。"),
            "state_destination": ("Jag ska till stan.", "I am going to town.", "我要去市中心。"),
            "ask_destination": (f"Går {transport} till {destination}?", f"Does {transport} go to {destination}?", f"{transport}去{destination}吗？"),
            "confirm_route": (f"Ja, {transport} går till {destination}.", f"Yes, {transport} goes to {destination}.", f"是的，{transport}去{destination}。"),
            "suggest_option": (f"Du kan ta {option}." if option else "Ta tåget.", f"You can take {option}." if option else "Take the train.", f"你可以坐{option}。" if option else "坐火车。"),
            "thank": ("Tack!", "Thank you!", "谢谢！"),
            "farewell": ("Hejdå!", "Goodbye!", "再见！"),
            "request_repeat": ("Kan du säga det igen?", "Can you say that again?", "你能再说一遍吗？"),
        }

        if func in templates:
            sv, en, zh = templates[func]
        elif speaker == "teacher":
            sv, en, zh = "Okej.", step.get("content_goal", "Okay."), "好的。"
        else:
            sv, en, zh = "Jag förstår.", step.get("content_goal", "I understand."), "我明白了。"

        return {
            "sentence": sv,
            "english": en,
            "chinese": zh,
            "function": func,
            "scenario": step.get("scenario", ""),
            "generated": True,
        }

    def retrieve_examples_for_plan(self, plan):
        """
        Retrieves top-3 relevant sentence examples for each turn in the plan
        using scenario and function matches with a 4-priority fallback loop.
        """
        scenario_id = plan["scenario"]
        sequence = plan["sequence"]
        
        RELATED_FUNCTIONS = {
            "greeting": ["introduce_name", "simple_first_meeting"],
            "offer_help": ["state_want", "ask_quantity", "state_quantity"],
            "state_want": ["state_quantity", "offer_help"],
            "ask_quantity": ["state_quantity", "state_want"],
            "state_quantity": ["ask_quantity", "state_want"],
            "state_price": ["ask_price", "pay_card"],
            "ask_permission": ["confirm_yes", "pay_card"],
            "confirm_yes": ["confirm_no", "ask_permission"],
            "state_problem": ["say_simple_symptom", "ask_help"],
            "ask_location": ["give_directions", "ask_route"],
            "give_directions": ["ask_location", "ask_route"],
            "introduce_name": ["greeting", "simple_first_meeting"],
            "say_languages": ["simple_first_meeting"],
            "ask_where_from": ["say_languages", "simple_first_meeting"]
        }
        
        retrieved_sequence = []
        for step in sequence:
            turn_num = step["turn"]
            speaker = step["speaker"]
            func = step["function"]
            goal = step["content_goal"]
            slots = step.get("required_slots", {})
            
            step_for_score = dict(step)
            step_for_score["scenario"] = scenario_id

            # Priority 1: same scenario + same function, ranked by slots/goal.
            examples = [
                s for s in self.sentence_examples
                if s.get("scenario") == scenario_id and s.get("function") == func
            ]
            examples = sorted(
                examples,
                key=lambda s: self._score_sentence_for_plan_step(s, step_for_score),
                reverse=True,
            )
            source = "Priority 1 (same scenario + same function + slot ranking)"

            slot_critical_functions = {
                "state_want",
                "state_need",
                "ask_item",
                "ask_quantity",
                "state_quantity",
                "state_price",
                "ask_permission",
                "ask_location",
                "give_location",
                "give_direction",
                "state_problem",
                "state_symptom",
                "ask_time",
                "state_time",
                "ask_destination",
                "confirm_route",
                "suggest_option",
            }
            if examples and func in slot_critical_functions and slots:
                top_blob = " ".join(
                    [
                        examples[0].get("sentence", ""),
                        examples[0].get("english", ""),
                        " ".join(examples[0].get("keywords", []) or []),
                        " ".join(str(v) for v in (examples[0].get("slots", {}) or {}).values()),
                    ]
                ).lower()
                stop_tokens = {"och", "att", "det", "den", "ett", "med", "till"}
                slot_tokens = [
                    token
                    for value in slots.values()
                    for token in re.findall(r"\b\w+\b", str(value).lower())
                    if len(token) > 2 and token not in stop_tokens
                ]
                if slot_tokens and not all(token in top_blob for token in slot_tokens):
                    examples = [self._fallback_sentence_for_step(step_for_score)] + examples[:2]
                    source = "Priority 1 + slot-aware generated lead example"

            if examples and func == "confirm_yes":
                examples = [self._fallback_sentence_for_step(step_for_score)] + examples[:2]
                source = "Priority 1 + teacher confirmation fallback"
            if examples and func == "give_location" and "child" in (goal or "").lower():
                examples = [self._fallback_sentence_for_step(step_for_score)] + examples[:2]
                source = "Priority 1 + child-location fallback"
            
            # Priority 2: same scenario + related function
            if not examples and func in RELATED_FUNCTIONS:
                related_funcs = RELATED_FUNCTIONS[func]
                examples = [s for s in self.sentence_examples if s.get("scenario") == scenario_id and s.get("function") in related_funcs]
                source = "Priority 2 (same scenario + related function)"
                
            # Priority 3: same scenario semantic fallback by goal/slots keywords
            if not examples:
                goal_text = (goal or "").lower()
                slot_text = " ".join(str(v) for v in slots.values()).lower()
                q_tokens = set(re.findall(r"\b\w+\b", f"{func} {goal_text} {slot_text}"))
                scenario_candidates = [
                    s for s in self.sentence_examples if s.get("scenario") == scenario_id
                ]
                ranked_candidates = []
                for cand in scenario_candidates:
                    c_tokens = set(
                        re.findall(
                            r"\b\w+\b",
                            " ".join(
                                [
                                    cand.get("sentence", ""),
                                    cand.get("english", ""),
                                    cand.get("function", ""),
                                    " ".join(cand.get("keywords", []) or []),
                                    " ".join(str(v) for v in (cand.get("slots", {}) or {}).values()),
                                ]
                            ).lower(),
                        )
                    )
                    overlap = len(q_tokens.intersection(c_tokens))
                    func_bonus = 2 if cand.get("function") == func else 0
                    slot_score = self._score_sentence_for_plan_step(cand, step_for_score)
                    ranked_candidates.append((overlap + func_bonus + slot_score, cand))
                ranked_candidates.sort(key=lambda x: x[0], reverse=True)
                examples = [c for score, c in ranked_candidates if score > 0][:3]
                source = "Priority 3 (same scenario semantic fallback)"

            # Priority 4: slot-aware generated fallback (avoid cross-scenario leakage)
            if not examples:
                examples = [self._fallback_sentence_for_step(step_for_score)]
                source = "Priority 4 (slot-aware generated fallback)"
                
            retrieved_sequence.append({
                "turn": turn_num,
                "speaker": speaker,
                "function": func,
                "content_goal": goal,
                "required_slots": slots,
                "source": source,
                "retrieved_examples": [{
                    "sentence": e["sentence"],
                    "english": e["english"],
                    "chinese": e["chinese"],
                    "function": e["function"],
                    "scenario": e["scenario"]
                } for e in examples[:3]] # limit to top 3 examples
            })
            
        return retrieved_sequence

    def _build_stages_from_retrieved_sequence(self, retrieved_sequence):
        """
        Deterministically builds coherent stages from plan retrieval sequence.
        Supports non-alternating speaker sequences in plans
        (e.g. teacher, teacher, learner) by grouping same-speaker turns.
        """
        stages = []
        stage_idx = 1

        def step_sentence(step):
            if step["retrieved_examples"]:
                ex = step["retrieved_examples"][0]
                return {
                    "sv": ex.get("sentence", ""),
                    "en": ex.get("english", ""),
                    "zh": ex.get("chinese", "")
                }
            # Structured fallback when retrieval misses.
            ex = self._fallback_sentence_for_step(step)
            return {"sv": ex["sentence"], "en": ex["english"], "zh": ex["chinese"]}

        def prompt_for_learner_step(step):
            func = step.get("function", "")
            slots = step.get("required_slots", {}) or {}
            item = slots.get("item", slots.get("place", "det"))
            person = slots.get("person", item)
            if person == "barn":
                person = "barnet"
            person_en = "the child" if person == "barnet" else person
            person_zh = "孩子" if person == "barnet" else person
            prompts = {
                "greeting": ("Hej!", "Hello!", "你好！"),
                "state_want": ("Vad vill du ha?", "What do you want?", "你想要什么？"),
                "state_need": ("Vad behöver du?", "What do you need?", "你需要什么？"),
                "ask_item": ("Kan jag hjälpa dig?", "Can I help you?", "我可以帮你吗？"),
                "ask_location": (f"Letar du efter {person}?", f"Are you looking for {person_en}?", f"你在找{person_zh}吗？"),
                "state_problem": ("Vad har hänt?", "What happened?", "发生了什么？"),
                "ask_help": ("Behöver du hjälp?", "Do you need help?", "你需要帮助吗？"),
                "state_symptom": ("Hur mår du?", "How do you feel?", "你感觉怎么样？"),
                "ask_time": ("Vad vill du fråga?", "What do you want to ask?", "你想问什么？"),
                "ask_destination": ("Vart ska du åka?", "Where are you going?", "你要去哪里？"),
                "ask_permission": ("Vad vill du göra?", "What do you want to do?", "你想做什么？"),
                "confirm_yes": ("Är det bra?", "Is that okay?", "这样可以吗？"),
                "thank": ("Varsågod.", "You are welcome.", "不客气。"),
                "farewell": ("Vi ses.", "See you.", "再见。"),
                "request_repeat": ("Förstår du?", "Do you understand?", "你明白吗？"),
            }
            sv, en, zh = prompts.get(func, ("Vad säger du?", "What do you say?", "你要怎么说？"))
            return {"sv": sv, "en": en, "zh": zh}

        current = {
            "sven_parts": [],
            "sven_en_parts": [],
            "sven_zh_parts": [],
            "target_parts": [],
            "target_en_parts": [],
            "target_zh_parts": [],
            "desc_parts": [],
            "intent": ""
        }

        def flush_current():
            nonlocal stage_idx, current
            if not current["sven_parts"] and not current["target_parts"]:
                return
            sven_phrase = " ".join(p for p in current["sven_parts"] if p).strip()
            target_phrase = " ".join(p for p in current["target_parts"] if p).strip()
            if not sven_phrase:
                sven_phrase = "Okej."
            if not target_phrase:
                if "hej då" in sven_phrase.lower() or "hejdå" in sven_phrase.lower():
                    target_phrase = "Hejdå!"
                    current["target_en_parts"].append("Goodbye!")
                    current["target_zh_parts"].append("再见！")
                else:
                    target_phrase = "Jag förstår."

            stages.append(
                {
                    "stage": stage_idx,
                    "desc": " -> ".join(current["desc_parts"]) if current["desc_parts"] else "Dialogue turn",
                    "intent": current["intent"] or "dialogue_turn",
                    "sven_phrase": sven_phrase,
                    "sven_english": " ".join(current["sven_en_parts"]).strip() or "Okay.",
                    "sven_chinese": " ".join(current["sven_zh_parts"]).strip() or "好的。",
                    "target_phrase": target_phrase,
                    "target_english": " ".join(current["target_en_parts"]).strip() or "I understand.",
                    "target_chinese": " ".join(current["target_zh_parts"]).strip() or "我明白了。"
                }
            )
            stage_idx += 1
            current = {
                "sven_parts": [],
                "sven_en_parts": [],
                "sven_zh_parts": [],
                "target_parts": [],
                "target_en_parts": [],
                "target_zh_parts": [],
                "desc_parts": [],
                "intent": ""
            }

        for step in retrieved_sequence:
            speaker = step["speaker"]
            text = step_sentence(step)
            if not current["intent"]:
                current["intent"] = step.get("function", "")
            current["desc_parts"].append(step.get("content_goal", ""))

            if speaker == "teacher":
                # If this stage already has learner side, start a fresh stage.
                if current["target_parts"]:
                    flush_current()
                    current["intent"] = step.get("function", "")
                    current["desc_parts"].append(step.get("content_goal", ""))
                current["sven_parts"].append(text["sv"])
                current["sven_en_parts"].append(text["en"])
                current["sven_zh_parts"].append(text["zh"])
            else:
                if not current["sven_parts"]:
                    prompt = prompt_for_learner_step(step)
                    current["sven_parts"].append(prompt["sv"])
                    current["sven_en_parts"].append(prompt["en"])
                    current["sven_zh_parts"].append(prompt["zh"])
                current["target_parts"].append(text["sv"])
                current["target_en_parts"].append(text["en"])
                current["target_zh_parts"].append(text["zh"])
                # Natural close condition: got both sides.
                if current["sven_parts"]:
                    flush_current()

        flush_current()
        return stages

    def _build_stage_blueprint_from_plan(self, plan, retrieved_sequence):
        """
        Build stage-level blueprint from plan sequence.
        Keeps plan order but converts variable speaker sequence into stage units
        with concrete seed sentences from retrieved examples.
        """
        if not plan:
            return []

        seq_by_turn = {s.get("turn"): s for s in (retrieved_sequence or [])}
        stages = []
        current = None

        for step in plan.get("sequence", []):
            turn = step.get("turn")
            speaker = step.get("speaker")
            ret = seq_by_turn.get(turn, {})
            ex = (ret.get("retrieved_examples") or [{}])[0]
            sv = ex.get("sentence", "")
            en = ex.get("english", "")
            zh = ex.get("chinese", "")

            if current is None:
                current = {
                    "desc_parts": [],
                    "intent": step.get("function", "dialogue_turn"),
                    "sven_seed": [],
                    "sven_en_seed": [],
                    "sven_zh_seed": [],
                    "target_seed": [],
                    "target_en_seed": [],
                    "target_zh_seed": [],
                }

            current["desc_parts"].append(step.get("content_goal", ""))
            if speaker == "teacher":
                if current["target_seed"]:
                    stages.append(current)
                    current = {
                        "desc_parts": [step.get("content_goal", "")],
                        "intent": step.get("function", "dialogue_turn"),
                        "sven_seed": [],
                        "sven_en_seed": [],
                        "sven_zh_seed": [],
                        "target_seed": [],
                        "target_en_seed": [],
                        "target_zh_seed": [],
                    }
                current["sven_seed"].append(sv)
                current["sven_en_seed"].append(en)
                current["sven_zh_seed"].append(zh)
            else:
                current["target_seed"].append(sv)
                current["target_en_seed"].append(en)
                current["target_zh_seed"].append(zh)
                if current["sven_seed"]:
                    stages.append(current)
                    current = None

        if current is not None:
            stages.append(current)

        normalized = []
        for idx, st in enumerate(stages, start=1):
            normalized.append(
                {
                    "stage": idx,
                    "desc": " -> ".join(p for p in st["desc_parts"] if p) or "Dialogue turn",
                    "intent": st["intent"],
                    "sven_seed": " ".join([x for x in st["sven_seed"] if x]).strip(),
                    "sven_en_seed": " ".join([x for x in st["sven_en_seed"] if x]).strip(),
                    "sven_zh_seed": " ".join([x for x in st["sven_zh_seed"] if x]).strip(),
                    "target_seed": " ".join([x for x in st["target_seed"] if x]).strip(),
                    "target_en_seed": " ".join([x for x in st["target_en_seed"] if x]).strip(),
                    "target_zh_seed": " ".join([x for x in st["target_zh_seed"] if x]).strip(),
                }
            )
        return normalized

    def _sanitize_generated_stages(self, stages, blueprint):
        """
        Enforce usable stage output for UI flow. If LLM omits fields, fill from seeds.
        """
        if not stages or not blueprint:
            return None
        fixed = []
        for idx, bp in enumerate(blueprint):
            raw = stages[idx] if idx < len(stages) and isinstance(stages[idx], dict) else {}
            sven_phrase = (raw.get("sven_phrase") or bp.get("sven_seed") or "").strip()
            target_phrase = (raw.get("target_phrase") or bp.get("target_seed") or "").strip()
            if not sven_phrase:
                sven_phrase = "Hej."
            if not target_phrase:
                target_phrase = "Jag förstår."
            if sven_phrase.lower() == target_phrase.lower():
                # Force distinction to keep quiz progression meaningful.
                target_phrase = bp.get("target_seed") or "Jag förstår."
            fixed.append(
                {
                    "stage": idx + 1,
                    "desc": bp.get("desc", raw.get("desc", "Dialogue turn")),
                    "intent": bp.get("intent", raw.get("intent", "dialogue_turn")),
                    "sven_phrase": sven_phrase,
                    "sven_english": (raw.get("sven_english") or bp.get("sven_en_seed") or "").strip(),
                    "sven_chinese": (raw.get("sven_chinese") or bp.get("sven_zh_seed") or "").strip(),
                    "target_phrase": target_phrase,
                    "target_english": (raw.get("target_english") or bp.get("target_en_seed") or "").strip(),
                    "target_chinese": (raw.get("target_chinese") or bp.get("target_zh_seed") or "").strip(),
                }
            )
        return fixed

    def _validate_stage_structure_against_plan(self, stages, plan):
        """
        Strict enough validation for stage quality without forcing perfect
        teacher/learner alternation at raw plan-step level.
        """
        if not stages or not plan:
            return False, ["Missing stages or plan."]
        seq = plan.get("sequence", [])
        issues = []
        if len(stages) < 3:
            issues.append("Too few dialogue stages (minimum 3 required).")
        if len(stages) > len(seq):
            issues.append("Too many dialogue stages compared to plan steps.")

        for i, stg in enumerate(stages):
            sven_phrase = (stg.get("sven_phrase") or "").strip().lower()
            target_phrase = (stg.get("target_phrase") or "").strip().lower()
            if not sven_phrase or not target_phrase:
                issues.append(f"Stage {i+1} has empty utterance.")
            if sven_phrase == target_phrase:
                issues.append(f"Stage {i+1} has duplicated Sven/learner phrase.")
        return len(issues) == 0, issues

    def _translation_for_stage_line(self, turn_data, line_owner, lang):
        """Returns the selected-language translation for a scripted stage line."""
        if line_owner == "sven":
            english = turn_data.get("sven_english", "")
            chinese = turn_data.get("sven_chinese", "")
            phrase = turn_data.get("sven_phrase", "")
        else:
            english = turn_data.get("target_english", "")
            chinese = turn_data.get("target_chinese", "")
            phrase = turn_data.get("target_phrase", "")

        if phrase in SVEN_TRANSLATIONS:
            english = english or SVEN_TRANSLATIONS[phrase].get("English", "")
            chinese = chinese or SVEN_TRANSLATIONS[phrase].get("Chinese", "")

        if lang == "Chinese":
            return chinese or english or "（暂无翻译）"
        return english or chinese or "Translation unavailable."

    def retrieve_topic_context(self, scenario_label, user_query=""):
        """
        User selects a UI topic tag → retrieve dialogue plans, sentences, vocabulary,
        and function schema → one LLM-ready context bundle + UI retrieval log.
        """
        self.add_thought(
            f"Structured retrieval for topic '{scenario_label}' (query: '{user_query}')"
        )

        if not self.dialogue_plans and not self.sentence_examples:
            self.add_thought("Structured datasets empty; topic context unavailable.")
            self.topic_context = None
            self.retrieved_examples_log = []
            return None

        self.topic_context = self.structured_retrieval.retrieve_topic_context(
            scenario_label=scenario_label,
            user_query=user_query,
            plan_selector=self.select_dialogue_plan,
            sequence_builder=self.retrieve_examples_for_plan,
        )

        plan = self.topic_context.get("plan")
        if plan:
            self.selected_plan_info = f"Plan: {plan['title']} | Goal: {plan['micro_goal']}"
            self.add_thought(f"Selected plan: {self.selected_plan_info}")
        else:
            self.selected_plan_info = ""
            self.add_thought("No dialogue plan matched; using scenario sentence bank only.")

        n_vocab = len(self.topic_context.get("vocabulary") or [])
        n_sents = len(self.topic_context.get("ranked_sentences") or [])
        n_turns = len(self.topic_context.get("retrieved_sequence") or [])
        self.add_thought(
            f"Context assembled: {n_vocab} vocab, {n_sents} ranked sentences, "
            f"{n_turns} plan turns with examples."
        )

        self.retrieved_examples_log = self.structured_retrieval.to_ui_log(
            self.topic_context, top_k=8
        )
        return self.topic_context

    def check_dialogue_coherence(self, stages, plan, scenario_id):
        """
        Performs rule-based dialogue coherence checks to prevent contradictions.
        Returns (is_coherent, list of issues).
        """
        issues = []
        if not isinstance(stages, list):
            return False, ["Output is not a JSON list of stages."]
            
        if len(stages) < 3:
            issues.append("Dialogue has too few stages (less than 3).")
            
        for idx, stage in enumerate(stages):
            if not isinstance(stage, dict):
                return False, ["One of the stages is not a dictionary."]
            required_keys = ["stage", "desc", "sven_phrase", "target_phrase"]
            for k in required_keys:
                if k not in stage:
                    issues.append(f"Stage {idx+1} is missing key: '{k}'")
                    
        all_texts = []
        for stage in stages:
            all_texts.append(stage.get("sven_phrase", "").lower())
            all_texts.append(stage.get("target_phrase", "").lower())
            all_texts.append(stage.get("sven_english", "").lower())
            all_texts.append(stage.get("target_english", "").lower())
            
        combined_text = " ".join(all_texts)
        
        # 1. Transport contradiction check
        if scenario_id == "transport":
            has_left = any(w in combined_text for w in ["left", "åkt", "missat", "missed", "bussen har åkt", "tåget har åkt"])
            buy_on_bus = any(w in combined_text for w in ["on the bus", "på bussen", "köpa biljett på bussen"])
            if has_left and buy_on_bus:
                issues.append("Contradiction detected: Dialog mentions the bus has left, but also mentions buying a ticket on the same bus.")
                
        # 2. Location query contradiction check
        for i, stage in enumerate(stages):
            sven_spoke = stage.get("sven_phrase", "").lower() + " " + stage.get("sven_english", "").lower()
            for j in range(i + 1, len(stages)):
                next_learner = stages[j].get("target_phrase", "").lower() + " " + stages[j].get("target_english", "").lower()
                if "station" in sven_spoke and "sjukhus" in sven_spoke:
                    if "var är sjukhuset" in next_learner or "where is the hospital" in next_learner:
                        issues.append("Contradiction: Learner asks 'where is the hospital' after Sven already explained its location.")
                if "hörnet" in sven_spoke or "corner" in sven_spoke:
                    if "var är busshållplatsen" in next_learner or "where is the bus stop" in next_learner:
                        issues.append("Contradiction: Learner asks 'where is the bus stop' after Sven already explained it is around the corner.")

        # 3. Scenario leakage check
        if scenario_id == "transport" and any(w in combined_text for w in ["äpple", "mjölk", "bröd", "doctor", "läkare"]):
            issues.append("Scenario leakage: Grocery or sickness vocabulary found inside transport scenario.")
        if scenario_id == "matbutik" and any(w in combined_text for w in ["doctor", "läkare", "busshållplatsen", "tunnelbana"]):
            issues.append("Scenario leakage: Sickness or transit vocabulary found inside grocery shop scenario.")
            
        if issues:
            return False, issues
        return True, []

    def parse_json_from_llm(self, response_text):
        """Extracts and parses JSON arrays from LLM response text."""
        if not response_text:
            return None
        match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
        if match:
            json_str = match.group(1)
        else:
            start_idx = response_text.find('[')
            end_idx = response_text.rfind(']')
            if start_idx != -1 and end_idx != -1:
                json_str = response_text[start_idx:end_idx+1]
            else:
                json_str = response_text
        
        try:
            return json.loads(json_str)
        except Exception as e:
            print(f"JSON parsing failed: {e}")
            return None

    def generate_coherent_dialogue(self, scenario_label, user_input, lang="English", topic_context=None):
        """
        Dialogue planner: structured topic retrieval → full context for LLM →
        coherence check → offline assembly from retrieved sentences if needed.
        """
        scenario_id = SCENARIO_MAPPING.get(scenario_label, scenario_label)

        if topic_context is None:
            topic_context = self.retrieve_topic_context(scenario_label, user_input)
        if not topic_context:
            print("No topic context. Falling back to legacy flow.")
            return None

        plan = topic_context.get("plan")
        if not plan:
            print("No dialogue plan in topic context. Falling back to legacy flow.")
            return None

        retrieved_sequence = topic_context.get("retrieved_sequence") or []
        blueprint = self._build_stage_blueprint_from_plan(plan, retrieved_sequence)
        num_stages = len(blueprint) if blueprint else max(3, (len(retrieved_sequence) + 1) // 2)
        context_block = topic_context.get("llm_context") or self.structured_retrieval.format_llm_context(
            topic_context
        )

        system_prompt = (
            "You are Sven, an immersive Swedish companion specializing in listening and reading comprehension for pre-A1 absolute beginners.\n"
            f"Active Scenario: '{scenario_id}'.\n"
            "Your task is to generate a complete, coherent Swedish dialogue practice script.\n"
            "A dialogue stage = one Sven line (teacher) + one expected learner reply.\n"
            f"Generate exactly {num_stages} stages that follow the SELECTED DIALOGUE PLAN turn sequence.\n\n"
            "DATA RULES (mandatory):\n"
            "1. Use ONLY vocabulary and sentences from the RETRIEVAL CONTEXT below (topic vocabulary, sentence bank, turn-by-turn examples).\n"
            "2. For each turn, prefer the listed TURN-BY-TURN RETRIEVED EXAMPLES verbatim; light edits for flow are OK.\n"
            "3. If a turn has no example, pick the closest line from the SCENARIO SENTENCE BANK — do not invent new topics or words.\n"
            "4. Respect each function's meaning from the DIALOGUE FUNCTIONS schema.\n\n"
            "COHERENCE RULES:\n"
            "1. Sven and learner lines must alternate naturally stage by stage.\n"
            "2. No contradictions across stages (e.g. bus already left → do not buy ticket on that bus).\n"
            "3. Keep Swedish pre-A1: short, clear sentences.\n"
            "4. NEVER use generic filler like only 'Hej' or 'Okej' for every stage.\n\n"
            "Output must be a JSON list of stages. Format your output EXACTLY like this:\n"
            "```json\n"
            "[\n"
            "  {\n"
            "    \"stage\": 1,\n"
            "    \"desc\": \"Greet the learner and offer help.\",\n"
            "    \"sven_phrase\": \"Sven's Swedish sentence here\",\n"
            "    \"sven_english\": \"Sven's English translation\",\n"
            "    \"sven_chinese\": \"Sven's Chinese translation\",\n"
            "    \"target_phrase\": \"User's expected Swedish reply\",\n"
            "    \"target_english\": \"User's expected English translation\",\n"
            "    \"target_chinese\": \"User's expected Chinese translation\"\n"
            "  },\n"
            "  ...\n"
            "]\n"
            "```\n"
            "Do not output any additional conversation, only the valid JSON array."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": (
                    f"Generate a {num_stages}-stage dialogue practice from this complete retrieval context.\n\n"
                    "STAGE BLUEPRINT (must preserve order and intent):\n"
                    f"{json.dumps(blueprint, ensure_ascii=False, indent=2)}\n\n"
                    f"{context_block}"
                ),
            },
        ]
        self.add_thought(
            f"LLM dialogue generation with unified context ({len(context_block)} chars)."
        )

        llm_response = ""
        stages = None
        
        if self.llm_provider and self.llm_available and config.USE_LLM_DIALOGUE_GENERATION:
            print("Invoking LLM dialogue planner...")
            llm_response = self.llm_provider.chat_complete(messages, temperature=0.2)
            stages = self.parse_json_from_llm(llm_response)
            stages = self._sanitize_generated_stages(stages, blueprint)
        elif self.llm_provider and self.llm_available:
            self.add_thought(
                "Stable demo mode: LLM dialogue generation is disabled; using retrieved plan/examples as the dialogue script."
            )
            
        if stages:
            is_coherent, issues = self.check_dialogue_coherence(stages, plan, scenario_id)
            is_structured, structure_issues = self._validate_stage_structure_against_plan(stages, plan)
            if not is_coherent or not is_structured:
                issues = (issues or []) + (structure_issues or [])
                print(f"⚠️ Coherence check failed. Issues found: {issues}")
                print("Invoking supportive revision loop to fix dialogue coherence...")
                
                messages.append({"role": "assistant", "content": llm_response})
                revision_query = (
                    "Your generated dialogue has the following coherence issues:\n"
                    + "\n".join([f"- {issue}" for issue in issues])
                    + "\n\nPlease revise the dialogue to fix these issues. "
                    "Make sure you keep the same plan, do not generate a totally new topic, "
                    "and return exactly the corrected JSON list of stages conforming to the same JSON format."
                )
                messages.append({"role": "user", "content": revision_query})
                
                revised_response = self.llm_provider.chat_complete(messages, temperature=0.3)
                revised_stages = self.parse_json_from_llm(revised_response)
                
                if revised_stages:
                    is_coherent_rev, issues_rev = self.check_dialogue_coherence(revised_stages, plan, scenario_id)
                    is_structured_rev, structure_issues_rev = self._validate_stage_structure_against_plan(revised_stages, plan)
                    if is_coherent_rev and is_structured_rev:
                        print("🟢 Coherence check PASSED after supportive revision loop!")
                        stages = revised_stages
                    else:
                        all_issues_rev = (issues_rev or []) + (structure_issues_rev or [])
                        print(f"⚠️ Revised dialogue still has issues: {all_issues_rev}. Using deterministic retrieval-based assembly.")
                        stages = None
                else:
                    print("🔴 Revised response JSON parsing failed. Using original generated version.")
                    stages = None
            else:
                print("🟢 Coherence check PASSED on the first attempt!")

        # 3. Fallback: deterministic assembly from retrieved sequence
        if not stages:
            print("🟢 Activating deterministic retrieval-based dialogue assembly fallback...")
            stages = self._build_stages_from_retrieved_sequence(retrieved_sequence)
            
        return stages

    def add_thought(self, thought_text):
        """Appends an internal reasoning step to the Thought Tracer log."""
        self.thought_logs.append(f"🤖 [THOUGHT] {thought_text}")
        print(f"[AGENT THOUGHT] {thought_text}")

    def initialize_provider(self, mode, ollama_endpoint=None, local_model=None, 
                            online_key=None, online_base=None, online_model=None):
        """Configures and runs connection checks on the LLM client provider."""
        self.add_thought(f"Configuring LLM Provider. Mode: {mode}")
        self.llm_provider = LLMProvider(
            mode=mode,
            ollama_endpoint=ollama_endpoint,
            local_model=local_model,
            online_key=online_key,
            online_base=online_base,
            online_model=online_model
        )
        is_ok, msg = self.llm_provider.check_connection()
        if is_ok:
            self.add_thought(f"LLM Provider online: {msg}")
        else:
            self.add_thought(f"LLM Provider connection failed: {msg}")
        self.llm_available = is_ok
        self.feedback_tool.set_llm_provider(self.llm_provider if is_ok else None)
        return is_ok, msg

    def _refresh_stage_retrieval_log(self, turn_data):
        """Keep Study Guide / IR table aligned with structured context for this stage."""
        intent = turn_data.get("intent", "")
        if self.topic_context:
            log = []
            for step in self.topic_context.get("retrieved_sequence") or []:
                if step.get("function") != intent:
                    continue
                for ex in step.get("retrieved_examples") or []:
                    log.append(
                        {
                            "text": ex.get("sentence", ""),
                            "english": ex.get("english", ""),
                            "chinese": ex.get("chinese", ""),
                            "base_score": 1.0,
                            "boost": 0.0,
                            "final_score": 1.0,
                            "source": f"plan_turn_{step.get('turn')}",
                        }
                    )
            if log:
                self.retrieved_examples_log = log[:4]
                self.add_thought(
                    f"Stage retrieval ({intent}): {len(log)} examples from dialogue plan."
                )
                return
            ranked = [
                s
                for s in self.topic_context.get("ranked_sentences") or []
                if s.get("function") == intent
            ][:4]
            if ranked:
                self.retrieved_examples_log = [
                    {
                        "text": s.get("sentence", ""),
                        "english": s.get("english", ""),
                        "chinese": s.get("chinese", ""),
                        "base_score": s.get("base_score", 0.0),
                        "boost": s.get("boost", 0.0),
                        "final_score": s.get("final_score", 0.0),
                        "source": f"sentence_bank:{intent}",
                    }
                    for s in ranked
                ]
                self.add_thought(
                    f"Stage retrieval ({intent}): {len(ranked)} sentences from topic bank."
                )
                return
        self.retrieved_examples_log = self.retrieval_tool.retrieve(
            self.current_scenario, intent, top_k=4
        )
        self.add_thought(f"Stage retrieval ({intent}): legacy IR fallback.")

    def get_preclass_guide(self, scenario_label, top_k=4):
        """
        Study guide phrases from the same structured topic retrieval used for dialogue.
        Falls back to legacy vector IR only if structured data is unavailable.
        """
        if self.topic_context and self.topic_context.get("scenario_label") == scenario_label:
            return self.structured_retrieval.to_ui_log(self.topic_context, top_k=top_k)
        if self.sentence_examples:
            ctx = self.structured_retrieval.build_topic_context(
                scenario_label,
                "standard dialogue",
                plan=None,
                retrieved_sequence=[],
            )
            return self.structured_retrieval.to_ui_log(ctx, top_k=top_k)
        return self.retrieval_tool.retrieve(scenario_label, "standard dialogue", top_k=top_k)

    def start_practice(self, scenario_label, quiz_type="multiple_choice", lang="English"):
        """
        Starts a daily-life roleplay scenario.
        Resets history, fetches pre-class reading guide, and builds greeting turn.
        """
        self.thought_logs = []
        self.retrieved_examples_log = []
        self.chat_history = []
        self.current_vocab_hints = ""
        self.current_scenario = scenario_label
        self.add_thought(f"Starting immersion practice for scenario: '{scenario_label}'")

        default_queries = {
            "food_shop": "Jag vill köpa mjölk och bröd.",
            "family_school": "Mitt barn går i skolan.",
            "health_places": "Jag är sjuk och behöver hjälp.",
            "transport": "Bussen har åkt. Jag vill åka till stan.",
            "home_places": "Var är köket?",
            "social_intro": "Hej, jag heter Sean.",
        }
        user_query = default_queries.get(scenario_label, "practice conversation")

        custom_stages = None
        self.selected_plan_info = ""
        self.topic_context = None

        if self.dialogue_plans or self.sentence_examples:
            self.add_thought(f"Topic '{scenario_label}': unified dataset retrieval, then LLM dialogue.")
            topic_context = self.retrieve_topic_context(scenario_label, user_query)
            if topic_context:
                stages = self.generate_coherent_dialogue(
                    scenario_label, user_query, lang, topic_context=topic_context
                )
                if stages:
                    custom_stages = stages
                    self.add_thought(
                        f"Dialogue ready from structured context: {self.selected_plan_info}"
                    )
                    for stg in stages:
                        SVEN_TRANSLATIONS[stg["sven_phrase"]] = {
                            "English": stg.get("sven_english", ""),
                            "Chinese": stg.get("sven_chinese", ""),
                        }

        # Dialogue stage reset
        self.active_turn_data = self.dialogue_tool.start_scenario(scenario_label, custom_stages=custom_stages)
        self.add_thought(f"Dialogue skeleton loaded. Stage 1/{self.dialogue_tool.max_stages}: {self.active_turn_data['desc']}")

        if not self.retrieved_examples_log:
            self.retrieved_examples_log = self.get_preclass_guide(scenario_label)
        
        sv_sentence = self.active_turn_data.get("sven_phrase", self.active_turn_data["target_phrase"])
        
        translation = self._translation_for_stage_line(self.active_turn_data, "sven", lang)
        
        self.current_translation = translation

        # Record assistant sentence to dialogue history
        self.chat_history.append({
            "role": "assistant",
            "content": sv_sentence,
            "english": self.active_turn_data.get("sven_english", ""),
            "chinese": self.active_turn_data.get("sven_chinese", ""),
        })
        self.add_thought(f"Avatar speaks: '{sv_sentence}' ({translation})")

        # Generate first response Quiz
        self.add_thought(f"Generating vocabulary quiz to let the user answer this turn ({quiz_type})...")
        self.active_quiz = self.quiz_tool.generate_quiz(
            scenario_label=scenario_label,
            target_sentence=self.active_turn_data["target_phrase"],
            quiz_type=quiz_type
        )
        
        # Build options vocabulary explanations INSTANTANEOUSLY via local dictionary
        self._build_options_vocab_hints(self.active_quiz["options"], lang)

        # Generate greeting TTS
        self.add_thought("Generating audio TTS voice synthesis for greeting...")
        audio_path = self.tts_avatar_tool.synthesize_swedish(sv_sentence)

        return {
            "avatar_state": "speaking",
            "avatar_sentence": sv_sentence,
            "translation": translation,
            "quiz_sentence": self.active_quiz["sentence_with_blank"],
            "options": self.active_quiz["options"],
            "correct_answer": self.active_quiz["correct_answer"],
            "stage_desc": self.active_turn_data["desc"],
            "stage_num": self.dialogue_tool.stage,
            "audio_path": audio_path,
            "vocab_hints": self.current_vocab_hints,
            "completed": False
        }

    def _build_options_vocab_hints(self, options, lang):
        """Compiles Swedish vocabulary explanations instantly in 0 ms using the offline dictionary."""
        self.add_thought("Instant offline dictionary lookup for options meanings...")
        hints = []
        for opt in options:
            opt_clean = opt.strip().lower().rstrip(".,!?")
            resolved = resolve_vocab(opt_clean, self.vocab_items, OFFLINE_DICT)
            meaning = resolved.get("english") or "vocabulary word"
            
            if lang == "Chinese":
                # Translate common ones to Chinese briefly
                cn_mappings = {
                    "apple": "苹果", "apples": "苹果（复数）", "coffee": "咖啡", "bread": "面包",
                    "bag": "袋子", "milk": "牛奶", "please": "请 / 谢谢", "cup": "杯子", "costs": "花费 / 价格",
                    "to buy": "购买", "tomatoes": "西红柿", "studies": "学习", "Swedish": "瑞典语",
                    "pen": "笔", "family": "家庭", "school": "学校", "teacher": "老师", "brother": "兄弟",
                    "sister": "姐妹", "feels": "感觉", "not": "不 / 否定", "good": "好", "hospital": "医院",
                    "the hospital": "医院", "the head": "头", "doctor": "医生", "medicine": "药",
                    "pain": "疼痛", "sick": "生病", "the pharmacy": "药店", "the bus stop": "公交车站",
                    "the train": "火车", "ticket": "票", "the bus": "公交车", "town": "市中心",
                    "the subway": "地铁", "the station": "车站", "fast": "快", "excuse me": "打扰一下",
                    "lives": "居住", "apartment": "公寓", "room": "房间", "the kitchen": "厨房",
                    "the toilet": "洗手间", "the house": "房子", "garden": "花园", "the sofa": "沙发",
                    "hello": "你好", "is named": "名叫", "nice": "很高兴", "to meet": "遇见", "where from": "来自哪里",
                    "comes": "来", "China": "中国", "speaks": "说", "little": "一点点", "how": "怎么 / 如何",
                    "you": "你", "I": "我", "name": "名字"
                }
                eng_part = meaning.split("(")[0].strip().replace("🔍 ", "").replace("🍎", "").replace("☕", "").replace("🍞", "").replace("🛍️", "").replace("🥛", "").replace("🙏", "").replace("💰", "").replace("🛒", "").replace("🍅", "").replace("📚", "").replace("🇸🇪", "").replace("✏", "").replace("👨‍👩‍👧‍👦", "").replace("🏫", "").replace("🧑‍🏫", "").replace("👦", "").replace("👧", "").replace("😊", "").replace("❌", "").replace("👍", "").replace("🏥", "").replace("🧠", "").replace("🩺", "").replace("💊", "").replace("🤕", "").replace("🤒", "").replace("🏪", "").replace("🚌", "").replace("🚆", "").replace("🎫", "").replace("🏙️", "").replace("🚇", "").replace("🚉", "").replace("🙋", "").replace("🏠", "").replace("🏢", "").replace("🔑", "").replace("🍳", "").replace("🚽", "").replace("🏡", "").replace("🛋️", "").replace("👋", "").replace("🏷️", "").replace("🤝", "").replace("🗺️", "").replace("🚶", "").replace("🇨🇳", "").replace("🗣️", "").replace("🤏", "").replace("❓", "").replace("👤", "")
                eng_part = eng_part.strip().lower()
                cn_meaning = resolved.get("chinese") or cn_mappings.get(eng_part, eng_part)
                hints.append(f"<b>{opt}</b> = {cn_meaning}")
            else:
                hints.append(f"<b>{opt}</b> = {meaning}")
                
        self.current_vocab_hints = " | ".join(hints)
        self.add_thought(f"Offline lookup complete: {self.current_vocab_hints}")

    def load_next_dialogue_turn(self, quiz_type="multiple_choice", lang="English"):
        """Advances the conversation state and prepares the next quiz."""
        self.add_thought("Advancing dialogue stage via 'Next Turn' click...")
        next_turn = self.dialogue_tool.next_turn()
        
        if not next_turn:
            self.add_thought("Conversation completed. No next turns.")
            return None

        self.active_turn_data = next_turn
        self.add_thought(f"Preparing next dialogue turn ({next_turn['stage']}/{self.dialogue_tool.max_stages}): '{next_turn['desc']}'")
        
        self._refresh_stage_retrieval_log(next_turn)

        sv_sentence = next_turn.get("sven_phrase", next_turn["target_phrase"])
        
        translation = self._translation_for_stage_line(next_turn, "sven", lang)

        # Invoke LLM only if not using pre-generated planner custom stages
        if not self.dialogue_tool.custom_stages:
            retrieved = self.retrieved_examples_log or []
            context_phrases = "\n".join([f"- Swedish: {item['text']} (Eng: {item['english']}, Chn: {item['chinese']})" for item in retrieved])
            history_str = "\n".join([f"{'User' if h['role']=='user' else 'Sven'}: {h['content']}" for h in self.chat_history])
            
            system_prompt = (
                "You are Sven, an immersive Swedish companion or shopkeeper specializing in listening and reading comprehension. The user is a beginner.\n"
                f"Scenario: '{self.current_scenario}'.\n"
                f"Current Dialogue Intent: '{next_turn['intent']}' ({next_turn['desc']}).\n"
                "Here is the dialogue history so far:\n"
                f"{history_str}\n\n"
                "Here are retrieved Swedish candidate phrases you can use as reference:\n"
                f"{context_phrases}\n\n"
                "Generate Sven's next short, natural response in Swedish that flows perfectly from the history. "
                f"Provide its direct translation in {lang}.\n"
                "Format your response EXACTLY like this:\n"
                "Sven: [One Swedish sentence here]\n"
                "Translation: [Translation here]"
            )

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "Respond to the user naturally in Swedish and ask the next question."}
            ]

            llm_response = ""
            if self.llm_provider and self.llm_available:
                self.add_thought("Invoking LLM to generate consistent next response...")
                llm_response = self.llm_provider.chat_complete(messages, temperature=0.6)
                self.add_thought("LLM Dialog Synthesis complete.")
            
            if llm_response and "Error:" not in llm_response:
                try:
                    lines = llm_response.split("\n")
                    for line in lines:
                        if line.lower().startswith("sven:"):
                            sv_sentence = line.split(":", 1)[1].strip()
                        elif line.lower().startswith("translation:"):
                            translation = line.split(":", 1)[1].strip()
                except Exception as e:
                    self.add_thought(f"Parsing LLM output failed: {e}.")
        
        self.current_translation = translation

        # Record assistant sentence to dialogue history
        self.chat_history.append({
            "role": "assistant",
            "content": sv_sentence,
            "english": next_turn.get("sven_english", ""),
            "chinese": next_turn.get("sven_chinese", ""),
        })
        self.add_thought(f"Avatar speaks: '{sv_sentence}' ({translation})")

        # Generate new quiz options
        self.active_quiz = self.quiz_tool.generate_quiz(
            scenario_label=self.current_scenario,
            target_sentence=next_turn["target_phrase"],
            quiz_type=quiz_type
        )
        self._build_options_vocab_hints(self.active_quiz["options"], lang)

        # Generate audio voice synthesis
        self.add_thought(f"Synthesizing Swedish speech narration: '{sv_sentence}'")
        audio_path = self.tts_avatar_tool.synthesize_swedish(sv_sentence)

        return {
            "avatar_state": "speaking",
            "avatar_sentence": sv_sentence,
            "translation": translation,
            "quiz_sentence": self.active_quiz["sentence_with_blank"],
            "options": self.active_quiz["options"],
            "correct_answer": self.active_quiz["correct_answer"],
            "stage_desc": self.active_turn_data["desc"],
            "stage_num": self.dialogue_tool.stage,
            "audio_path": audio_path,
            "vocab_hints": self.current_vocab_hints,
            "completed": False
        }

    def process_answer(self, user_answer, lang="English"):
        """Processes user response: validates, captures weights, and updates Sven visual states."""
        self.add_thought(f"User submitted answer: '{user_answer}'")
        
        correct_ans = self.active_quiz["correct_answer"]
        target_word = self.active_quiz["target_word"]
        
        is_correct, feedback_txt = self.feedback_tool.check_answer(
            scenario_label=self.current_scenario,
            user_answer=user_answer,
            correct_answer=correct_ans,
            target_word=target_word,
            lang=lang
        )

        if is_correct:
            avatar_state = "happy"
            self.add_thought("Correct answer! Sven is happy.")
            
            user_sentence = self.active_turn_data["target_phrase"]
            user_translation = self._translation_for_stage_line(self.active_turn_data, "target", lang)
            self.chat_history.append({
                "role": "user",
                "content": user_sentence,
                "english": self.active_turn_data.get("target_english", ""),
                "chinese": self.active_turn_data.get("target_chinese", ""),
            })
            
            self.add_thought(f"Synthesizing complete Swedish sentence vocal: '{user_sentence}'")
            audio_path = self.tts_avatar_tool.synthesize_swedish(user_sentence)
            
            completed = self.dialogue_tool.is_completed()
        else:
            avatar_state = "correcting"
            self.add_thought("Incorrect answer. Sven will present a supportive correction.")
            user_sentence = self.active_turn_data["target_phrase"]
            user_translation = self._translation_for_stage_line(self.active_turn_data, "target", lang)
            self.add_thought(f"Synthesizing correct target sentence for review: '{user_sentence}'")
            audio_path = self.tts_avatar_tool.synthesize_swedish(user_sentence)
            completed = False

        sv_sentence = user_sentence if not is_correct else (self.chat_history[-1]["content"] if self.chat_history else "Svenska")

        return {
            "is_correct": is_correct,
            "avatar_state": avatar_state,
            "feedback_text": feedback_txt,
            "audio_path": audio_path,
            "avatar_sentence": sv_sentence,
            "translation": user_translation if is_correct else self.current_translation,
            "quiz_sentence": self.active_quiz["sentence_with_blank"] if not completed else "",
            "options": self.active_quiz["options"] if not completed else [],
            "correct_answer": self.active_quiz["correct_answer"] if not completed else "",
            "stage_desc": self.active_turn_data["desc"] if not completed else "Completed!",
            "stage_num": self.dialogue_tool.stage,
            "vocab_hints": self.current_vocab_hints if not completed else "",
            "completed": completed
        }

if __name__ == "__main__":
    agent = SwedishSpeakingAgent()
    agent.initialize_provider("Local Mode")
