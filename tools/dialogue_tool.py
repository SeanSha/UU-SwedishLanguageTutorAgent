import config

SCENARIO_SKELETONS = {
    "food_shop": [
        {"stage": 1, "desc": "Greet the shopkeeper", "intent": "greeting", "sven_phrase": "Hej! Välkommen till matbutiken. Kan jag hjälpa dig?", "target_phrase": "Hej!"},
        {"stage": 2, "desc": "Say what you want to buy", "intent": "buy_item", "sven_phrase": "Vad vill du köpa idag?", "target_phrase": "Jag vill ha ett äpple."},
        {"stage": 3, "desc": "Ask how much it costs", "intent": "ask_price", "sven_phrase": "Här är äpplet. Något mer?", "target_phrase": "Vad kostar det?"},
        {"stage": 4, "desc": "Ask for a shopping bag", "intent": "ask_bag", "sven_phrase": "Det kostar tio kronor. Vill du ha en påse?", "target_phrase": "Kan jag få en påse?"},
        {"stage": 5, "desc": "Thank them and say goodbye", "intent": "goodbye", "sven_phrase": "Ja, här är påsen. Det blir tio kronor.", "target_phrase": "Tack, hejdå!"}
    ],
    "social_intro": [
        {"stage": 1, "desc": "Say hi and state your name", "intent": "greeting", "sven_phrase": "Hej! Jag heter Sven. Vad heter du?", "target_phrase": "Hej! Vad heter du?"},
        {"stage": 2, "desc": "Say where you come from", "intent": "origin", "sven_phrase": "Trevligt att träffas! Varifrån kommer du?", "target_phrase": "Jag kommer från Kina."},
        {"stage": 3, "desc": "Say you speak a little Swedish", "intent": "language", "sven_phrase": "Vad roligt! Talar du svenska?", "target_phrase": "Jag talar lite svenska."},
        {"stage": 4, "desc": "Ask how they are doing", "intent": "ask_health", "sven_phrase": "Ja, du talar jättebra! Hur mår du idag?", "target_phrase": "Hur mår du?"},
        {"stage": 5, "desc": "Say nice to meet you and goodbye", "intent": "goodbye", "sven_phrase": "Jag mår också bra, tack! Vi ses!", "target_phrase": "Trevligt att träffas, hejdå!"}
    ],
    "family_school": [
        {"stage": 1, "desc": "Greet and state that you study Swedish", "intent": "studies", "sven_phrase": "Hej! Vad gör du på fritiden?", "target_phrase": "Jag studerar svenska."},
        {"stage": 2, "desc": "Ask if they have a pen", "intent": "ask_pen", "sven_phrase": "Vad spännande! Skriver du mycket?", "target_phrase": "Har du en penna?"},
        {"stage": 3, "desc": "Introduce your family", "intent": "family", "sven_phrase": "Ja, här är en penna. Bor du med kompisar?", "target_phrase": "Det här är min familj."},
        {"stage": 4, "desc": "Ask who their teacher is", "intent": "ask_teacher", "sven_phrase": "Vilken fin familj! Går du i skolan?", "target_phrase": "Vem är din lärare?"},
        {"stage": 5, "desc": "State that you have a brother and say goodbye", "intent": "brother", "sven_phrase": "Min lärare heter Maria. Har du syskon?", "target_phrase": "Jag har en bror, hejdå!"}
    ],
    "health_places": [
        {"stage": 1, "desc": "State that you don't feel well", "intent": "not_well", "sven_phrase": "Hej! Hur mår du idag?", "target_phrase": "Jag mår inte bra."},
        {"stage": 2, "desc": "Say you have a headache", "intent": "headache", "sven_phrase": "Vad tråkigt att höra. Var har du ont?", "target_phrase": "Jag har ont i huvudet."},
        {"stage": 3, "desc": "Ask where the hospital is", "intent": "ask_hospital", "sven_phrase": "Du kanske behöver åka till sjukhuset.", "target_phrase": "Var är sjukhuset?"},
        {"stage": 4, "desc": "Say you need a doctor", "intent": "need_doctor", "sven_phrase": "Det ligger nära stationen. Vill du träffa en läkare?", "target_phrase": "Jag behöver en läkare."},
        {"stage": 5, "desc": "Say you need medicine and goodbye", "intent": "need_medicine", "sven_phrase": "Okej, jag ringer en läkare nu. Krya på dig!", "target_phrase": "Jag behöver medicin, tack!"}
    ],
    "transport": [
        {"stage": 1, "desc": "Ask where the bus stop is", "intent": "bus_stop", "sven_phrase": "Ursäkta, bussen har åkt.", "target_phrase": "Var är busshållplatsen?"},
        {"stage": 2, "desc": "State that you want to buy a ticket", "intent": "buy_ticket", "sven_phrase": "Den är runt hörnet. Ska du åka långt?", "target_phrase": "Jag vill köpa en biljett."},
        {"stage": 3, "desc": "Ask if this bus goes to town", "intent": "ask_direction", "sven_phrase": "Du kan köpa den på bussen. Vart ska du åka?", "target_phrase": "Går den här bussen till stan?"},
        {"stage": 4, "desc": "Remark that the subway is fast", "intent": "subway", "sven_phrase": "Ja, men tåget är snabbare.", "target_phrase": "Tunnelbanan är snabb."},
        {"stage": 5, "desc": "Ask where the station is and thank them", "intent": "station", "sven_phrase": "Ja, tunnelbanan är mycket snabb. Stationen är nära.", "target_phrase": "Ursäkta, var är stationen? Tack!"}
    ],
    "home_places": [
        {"stage": 1, "desc": "State that you live in an apartment", "intent": "apartment", "sven_phrase": "Hej! Välkommen hem till mig. Var bor du?", "target_phrase": "Jag bor i en lägenhet."},
        {"stage": 2, "desc": "Introduce your room", "intent": "room", "sven_phrase": "Vad trevligt! Kom in, så visar jag huset.", "target_phrase": "Det här är mitt rum."},
        {"stage": 3, "desc": "Say that the kitchen is small", "intent": "kitchen", "sven_phrase": "Fint rum! Här är köket.", "target_phrase": "Köket är litet."},
        {"stage": 4, "desc": "Ask where the toilet is", "intent": "ask_toilet", "sven_phrase": "Ja, men det fungerar bra. Behöver du tvätta händerna?", "target_phrase": "Var är toaletten?"},
        {"stage": 5, "desc": "State that the house has a garden and say goodbye", "intent": "garden", "sven_phrase": "Den är till vänster. Kolla, vi har en stor trädgård.", "target_phrase": "Huset har en trädgård, hejdå!"}
    ]
}

class DialogueTool:
    """
    Tracks dialog progression stages dynamically (supporting both classic 5-turn hardcoded skeletons
    and custom planner-generated plan sequences of arbitrary length).
    """
    def __init__(self):
        self.stage = 1
        self.max_stages = 5
        self.active_scenario = None
        self.custom_stages = None

    def start_scenario(self, scenario_label, custom_stages=None):
        """Initializes a new dialogue scenario, optionally accepting custom pre-generated stages."""
        if scenario_label not in SCENARIO_SKELETONS:
            scenario_label = "food_shop"
        self.active_scenario = scenario_label
        self.stage = 1
        
        if custom_stages:
            self.custom_stages = custom_stages
            self.max_stages = len(custom_stages)
        else:
            self.custom_stages = None
            self.max_stages = 5
            
        if self.custom_stages:
            return self.custom_stages[0]
        return SCENARIO_SKELETONS[scenario_label][0]

    def next_turn(self):
        """Advances to the next stage in the dialogue."""
        if self.stage < self.max_stages:
            self.stage += 1
            if self.custom_stages:
                return self.custom_stages[self.stage - 1]
            return SCENARIO_SKELETONS[self.active_scenario][self.stage - 1]
        return None

    def get_current_turn_data(self):
        """Retrieves details of the active stage."""
        if not self.active_scenario:
            return None
        if self.custom_stages:
            return self.custom_stages[self.stage - 1]
        return SCENARIO_SKELETONS[self.active_scenario][self.stage - 1]

    def is_completed(self):
        """Checks if the scenario is finished."""
        return self.stage >= self.max_stages

if __name__ == "__main__":
    dt = DialogueTool()
    first = dt.start_scenario("food_shop")
    print("Stage 1:", first)
    nxt = dt.next_turn()
    print("Stage 2:", nxt)
