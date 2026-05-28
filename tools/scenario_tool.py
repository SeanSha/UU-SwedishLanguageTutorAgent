import os
import pandas as pd
from datasets import load_dataset
import config

# High-quality fallback dataset for offline running
FALLBACK_DATA = [
    # food_shop
    {"text": "Jag vill ha ett äpple.", "english": "I want an apple.", "chinese": "我想要一个苹果。", "label": "food_shop", "lecture_theme": "Ordering Food", "source": "local_fallback", "review_status": "approved"},
    {"text": "Vad kostar det?", "english": "How much does it cost?", "chinese": "这卖多少钱？", "label": "food_shop", "lecture_theme": "Price Inquiries", "source": "local_fallback", "review_status": "approved"},
    {"text": "Kan jag få en påse?", "english": "Can I get a bag?", "chinese": "可以给我一个袋子吗？", "label": "food_shop", "lecture_theme": "Checkout", "source": "local_fallback", "review_status": "approved"},
    {"text": "En kopp kaffe, tack.", "english": "A cup of coffee, please.", "chinese": "请给我一杯咖啡。", "label": "food_shop", "lecture_theme": "Café", "source": "local_fallback", "review_status": "approved"},
    {"text": "Jag vill köpa bröd.", "english": "I want to buy bread.", "chinese": "我想要买面包。", "label": "food_shop", "lecture_theme": "Bakery", "source": "local_fallback", "review_status": "approved"},
    {"text": "Har ni mjölk?", "english": "Do you have milk?", "chinese": "你们有牛奶吗？", "label": "food_shop", "lecture_theme": "Grocery", "source": "local_fallback", "review_status": "approved"},
    # family_school
    {"text": "Jag studerar svenska.", "english": "I study Swedish.", "chinese": "我学习瑞典语。", "label": "family_school", "lecture_theme": "Studies", "source": "local_fallback", "review_status": "approved"},
    {"text": "Har du en penna?", "english": "Do you have a pen?", "chinese": "你有笔吗？", "label": "family_school", "lecture_theme": "School supplies", "source": "local_fallback", "review_status": "approved"},
    {"text": "Det här är min familj.", "english": "This is my family.", "chinese": "这是我的家人。", "label": "family_school", "lecture_theme": "Family", "source": "local_fallback", "review_status": "approved"},
    {"text": "Min skola är stor.", "english": "My school is big.", "chinese": "我的学校很大。", "label": "family_school", "lecture_theme": "School", "source": "local_fallback", "review_status": "approved"},
    {"text": "Vem är din lärare?", "english": "Who is your teacher?", "chinese": "你的老师是谁？", "label": "family_school", "lecture_theme": "School", "source": "local_fallback", "review_status": "approved"},
    {"text": "Jag har en bror.", "english": "I have a brother.", "chinese": "我有一个兄弟。", "label": "family_school", "lecture_theme": "Family", "source": "local_fallback", "review_status": "approved"},
    # health_places
    {"text": "Jag mår inte bra.", "english": "I don't feel well.", "chinese": "我感觉不舒服。", "label": "health_places", "lecture_theme": "Health", "source": "local_fallback", "review_status": "approved"},
    {"text": "Var är sjukhuset?", "english": "Where is the hospital?", "chinese": "医院在哪里？", "label": "health_places", "lecture_theme": "Places", "source": "local_fallback", "review_status": "approved"},
    {"text": "Jag har ont i huvudet.", "english": "I have a headache.", "chinese": "我头疼。", "label": "health_places", "lecture_theme": "Sickness", "source": "local_fallback", "review_status": "approved"},
    {"text": "Jag behöver en läkare.", "english": "I need a doctor.", "chinese": "我需要医生。", "label": "health_places", "lecture_theme": "Medical Help", "source": "local_fallback", "review_status": "approved"},
    {"text": "Apoteket är öppet.", "english": "The pharmacy is open.", "chinese": "药店开着。", "label": "health_places", "lecture_theme": "Places", "source": "local_fallback", "review_status": "approved"},
    {"text": "Jag behöver medicin.", "english": "I need medicine.", "chinese": "我需要药。", "label": "health_places", "lecture_theme": "Medical Help", "source": "local_fallback", "review_status": "approved"},
    # transport
    {"text": "Var är busshållplatsen?", "english": "Where is the bus stop?", "chinese": "公交车站在哪里？", "label": "transport", "lecture_theme": "Transit Stop", "source": "local_fallback", "review_status": "approved"},
    {"text": "Tåget går klockan nio.", "english": "The train leaves at nine o'clock.", "chinese": "火车九点出发。", "label": "transport", "lecture_theme": "Schedule", "source": "local_fallback", "review_status": "approved"},
    {"text": "Jag vill köpa en biljett.", "english": "I want to buy a ticket.", "chinese": "我想买张票。", "label": "transport", "lecture_theme": "Buying tickets", "source": "local_fallback", "review_status": "approved"},
    {"text": "Går den här bussen till stan?", "english": "Does this bus go to town?", "chinese": "这辆公交车去市中心吗？", "label": "transport", "lecture_theme": "Directions", "source": "local_fallback", "review_status": "approved"},
    {"text": "Tunnelbanan är snabb.", "english": "The subway is fast.", "chinese": "地铁很快。", "label": "transport", "lecture_theme": "Subway", "source": "local_fallback", "review_status": "approved"},
    {"text": "Ursäkta, var är stationen?", "english": "Excuse me, where is the station?", "chinese": "请问，车站在哪里？", "label": "transport", "lecture_theme": "Directions", "source": "local_fallback", "review_status": "approved"},
    # home_places
    {"text": "Jag bor i en lägenhet.", "english": "I live in an apartment.", "chinese": "我住在一个公寓里。", "label": "home_places", "lecture_theme": "Living Space", "source": "local_fallback", "review_status": "approved"},
    {"text": "Det här är mitt rum.", "english": "This is my room.", "chinese": "这是我的房间。", "label": "home_places", "lecture_theme": "Rooms", "source": "local_fallback", "review_status": "approved"},
    {"text": "Köket är litet.", "english": "The kitchen is small.", "chinese": "厨房很小。", "label": "home_places", "lecture_theme": "Rooms", "source": "local_fallback", "review_status": "approved"},
    {"text": "Var är toaletten?", "english": "Where is the toilet?", "chinese": "洗手间在哪里？", "label": "home_places", "lecture_theme": "Rooms", "source": "local_fallback", "review_status": "approved"},
    {"text": "Huset har en trädgård.", "english": "The house has a garden.", "chinese": "房子有一个花园。", "label": "home_places", "lecture_theme": "House", "source": "local_fallback", "review_status": "approved"},
    {"text": "Soffan är bekväm.", "english": "The sofa is comfortable.", "chinese": "沙发很舒服。", "label": "home_places", "lecture_theme": "Furniture", "source": "local_fallback", "review_status": "approved"},
    # social_intro
    {"text": "Hej! Vad heter du?", "english": "Hi! What is your name?", "chinese": "你好！你叫什么名字？", "label": "social_intro", "lecture_theme": "Greetings", "source": "local_fallback", "review_status": "approved"},
    {"text": "Trevligt att träffas.", "english": "Nice to meet you.", "chinese": "很高兴见到你。", "label": "social_intro", "lecture_theme": "Greetings", "source": "local_fallback", "review_status": "approved"},
    {"text": "Varifrån kommer du?", "english": "Where are you from?", "chinese": "你来自哪里？", "label": "social_intro", "lecture_theme": "Introductions", "source": "local_fallback", "review_status": "approved"},
    {"text": "Jag kommer från Kina.", "english": "I come from China.", "chinese": "我来自中国。", "label": "social_intro", "lecture_theme": "Introductions", "source": "local_fallback", "review_status": "approved"},
    {"text": "Jag talar lite svenska.", "english": "I speak a little Swedish.", "chinese": "我会说一点瑞典语。", "label": "social_intro", "lecture_theme": "Languages", "source": "local_fallback", "review_status": "approved"},
    {"text": "Hur mår du?", "english": "How are you?", "chinese": "你好吗？", "label": "social_intro", "lecture_theme": "Greetings", "source": "local_fallback", "review_status": "approved"}
]

class ScenarioTool:
    """
    Handles loading, caching, and filtering the Hugging Face Swedish Pre-A1 Scenario Classifier dataset.
    """
    def __init__(self):
        self.df = None
        self.load_dataset()

    def load_dataset(self):
        """
        Attempts to load from the local cache file, and if not present, pulls from Hugging Face datasets.
        Falls back to local fallback list in case of network errors.
        """
        # 1. Try Cache File first
        if os.path.exists(config.DATASET_CACHE_PATH):
            try:
                self.df = pd.read_csv(config.DATASET_CACHE_PATH)
                print(f"Loaded dataset from cache: {config.DATASET_CACHE_PATH} ({len(self.df)} rows)")
                return
            except Exception as e:
                print(f"Error reading dataset cache: {e}. Re-fetching...")

        # 2. Try loading from Hugging Face
        try:
            print(f"Attempting to fetch dataset '{config.HF_DATASET_ID}' from Hugging Face...")
            hf_dataset = load_dataset(config.HF_DATASET_ID)
            
            # Combine all splits if multiple splits exist
            dfs = []
            for split in hf_dataset.keys():
                dfs.append(hf_dataset[split].to_pandas())
            
            self.df = pd.concat(dfs, ignore_index=True)
            print(f"Successfully loaded dataset from HF! Rows: {len(self.df)}")
            
            # Ensure required directories exist and cache dataset
            os.makedirs(os.path.dirname(config.DATASET_CACHE_PATH), exist_ok=True)
            self.df.to_csv(config.DATASET_CACHE_PATH, index=False)
            print(f"Cached dataset locally to: {config.DATASET_CACHE_PATH}")
            return
        except Exception as e:
            print(f"Failed to fetch from Hugging Face: {e}.")
            print("Falling back to local high-quality offline vocabulary dataset.")
            
        # 3. Fallback to offline data
        self.df = pd.DataFrame(FALLBACK_DATA)
        # Cache fallback so we don't spam print next time
        try:
            os.makedirs(os.path.dirname(config.DATASET_CACHE_PATH), exist_ok=True)
            self.df.to_csv(config.DATASET_CACHE_PATH, index=False)
        except Exception:
            pass

    def get_sentences_by_scenario(self, scenario_label):
        """
        Filters the dataset by scenario label and returns a list of dictionaries.
        """
        if self.df is None or self.df.empty:
            return []
            
        filtered = self.df[self.df["label"] == scenario_label]
        # Fallback if filtered is empty for some reason
        if filtered.empty:
            filtered = pd.DataFrame([d for d in FALLBACK_DATA if d["label"] == scenario_label])
            
        return filtered.to_dict(orient="records")

if __name__ == "__main__":
    tool = ScenarioTool()
    print("Available Scenarios:")
    for sc in config.SCENARIOS:
        rows = tool.get_sentences_by_scenario(sc)
        print(f"- {sc}: {len(rows)} examples found. Example 1: {rows[0]['text'] if rows else 'None'}")
