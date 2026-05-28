import re


EXTRA_GLOSSARY = {
    "akut": {"english": "emergency/urgent", "chinese": "紧急"},
    "betala": {"english": "pay", "chinese": "付款"},
    "betalar": {"english": "pay/pays", "chinese": "付款"},
    "betyder": {"english": "means", "chinese": "意思是"},
    "billigt": {"english": "cheap", "chinese": "便宜的"},
    "boka": {"english": "book/reserve", "chinese": "预约"},
    "börjar": {"english": "starts/begins", "chinese": "开始"},
    "ditt": {"english": "your", "chinese": "你的"},
    "dyrt": {"english": "expensive", "chinese": "贵的"},
    "efter": {"english": "after", "chinese": "之后"},
    "gammal": {"english": "old", "chinese": "老的/岁"},
    "gång": {"english": "time/occasion", "chinese": "次"},
    "heter": {"english": "is named/called", "chinese": "叫做"},
    "hemma": {"english": "at home", "chinese": "在家"},
    "hämta": {"english": "pick up/fetch", "chinese": "接/取"},
    "hämtar": {"english": "pick up/fetch", "chinese": "接/取"},
    "idag": {"english": "today", "chinese": "今天"},
    "ifrån": {"english": "from", "chinese": "来自"},
    "igen": {"english": "again", "chinese": "再次"},
    "imorgon": {"english": "tomorrow", "chinese": "明天"},
    "kallt": {"english": "cold", "chinese": "冷的"},
    "kassan": {"english": "checkout/cash register", "chinese": "收银台"},
    "kina": {"english": "China", "chinese": "中国"},
    "klockan": {"english": "o'clock/time", "chinese": "点钟"},
    "kontant": {"english": "cash", "chinese": "现金"},
    "kort": {"english": "card/short", "chinese": "卡/短的"},
    "kostar": {"english": "costs", "chinese": "花费"},
    "kronor": {"english": "kronor", "chinese": "克朗"},
    "leker": {"english": "plays", "chinese": "玩"},
    "letar": {"english": "looks for", "chinese": "寻找"},
    "lina": {"english": "Lina", "chinese": "莉娜"},
    "lite": {"english": "a little", "chinese": "一点"},
    "litet": {"english": "small", "chinese": "小的"},
    "lämnar": {"english": "leave/drop off", "chinese": "留下/送下"},
    "många": {"english": "many", "chinese": "很多"},
    "missade": {"english": "missed", "chinese": "错过了"},
    "prata": {"english": "talk", "chinese": "说话"},
    "ring": {"english": "call", "chinese": "打电话"},
    "skriv": {"english": "write", "chinese": "写"},
    "snart": {"english": "soon", "chinese": "很快"},
    "stockholm": {"english": "Stockholm", "chinese": "斯德哥尔摩"},
    "stan": {"english": "town/city center", "chinese": "市中心"},
    "student": {"english": "student", "chinese": "学生"},
    "stort": {"english": "big/large", "chinese": "大的"},
    "stängt": {"english": "closed", "chinese": "关门的"},
    "sverige": {"english": "Sweden", "chinese": "瑞典"},
    "säga": {"english": "say", "chinese": "说"},
    "tjugo": {"english": "twenty", "chinese": "二十"},
    "träffa": {"english": "meet", "chinese": "见面"},
    "träffas": {"english": "meet", "chinese": "见面"},
    "uppsala": {"english": "Uppsala", "chinese": "乌普萨拉"},
    "varmt": {"english": "warm", "chinese": "暖的"},
    "vart": {"english": "where to", "chinese": "去哪里"},
    "väskan": {"english": "the bag", "chinese": "包"},
    "vården": {"english": "health care", "chinese": "医疗护理"},
    "öppen": {"english": "open", "chinese": "开着的"},
}


def clean_word(word):
    return (word or "").strip().lower().rstrip(".,!?;:")


def clean_offline_meaning(meaning):
    meaning = re.sub(r"[\U00010000-\U0010ffff\u2600-\u27ff\ufe0f]", "", meaning or "").strip()
    return meaning.split(" (", 1)[0].strip()


def surface_forms_for_item(item):
    """Generates common pre-A1 Swedish surface forms for a vocabulary item."""
    base = clean_word(item.get("word"))
    pos = (item.get("part_of_speech") or "").lower()
    forms = {base}
    if not base:
        return forms

    # Common definite noun/adjective surfaces in the dataset sentences.
    forms.update({base + "en", base + "et", base + "n", base + "t"})
    if base.endswith("a"):
        forms.update({base + "n", base[:-1] + "an", base[:-1] + "or"})
    if base.endswith("e"):
        forms.add(base + "n")
    if base.endswith("m"):
        forms.add(base + "met")
    if base.endswith("er") and len(base) > 3:
        forms.add(base[:-2] + "ret")
    if base.endswith("an"):
        forms.add(base + "er")
    forms.update({base + "ar", base + "er", base + "r", base + "n"})

    if pos == "verb" or base.endswith(("a", "å", "o")):
        stem = base[:-1] if base.endswith("a") else base
        forms.update({stem + "ar", stem + "er", stem + "r"})
        verb_specials = {
            "bo": "bor",
            "förstå": "förstår",
            "gå": "går",
            "hjälpa": "hjälper",
            "komma": "kommer",
            "köpa": "köper",
            "leka": "leker",
            "läsa": "läser",
            "ringa": "ringer",
            "skriva": "skriver",
            "tala": "talar",
            "åka": "åker",
        }
        if base in verb_specials:
            forms.add(verb_specials[base])

    return {f for f in forms if f}


def resolve_vocab(word, vocab_items=None, offline_dict=None):
    """
    Resolves a displayed Swedish word form to a learner-safe meaning.
    Returns item/base form when available; otherwise falls back to dictionaries.
    """
    target = clean_word(word)
    vocab_items = vocab_items or []
    offline_dict = offline_dict or {}

    for item in vocab_items:
        if clean_word(item.get("word")) == target:
            return {
                "word": target,
                "base": clean_word(item.get("word")),
                "english": item.get("english", ""),
                "chinese": item.get("chinese", ""),
                "example": item.get("example_sentence", ""),
                "item": item,
                "source": "vocabulary_exact",
            }

    for item in vocab_items:
        if target in surface_forms_for_item(item):
            return {
                "word": target,
                "base": clean_word(item.get("word")),
                "english": item.get("english", ""),
                "chinese": item.get("chinese", ""),
                "example": item.get("example_sentence", ""),
                "item": item,
                "source": "vocabulary_surface",
            }

    if target in EXTRA_GLOSSARY:
        data = EXTRA_GLOSSARY[target]
        return {
            "word": target,
            "base": target,
            "english": data.get("english", ""),
            "chinese": data.get("chinese", ""),
            "example": "",
            "item": {},
            "source": "extra_glossary",
        }

    if target in offline_dict:
        return {
            "word": target,
            "base": target,
            "english": clean_offline_meaning(offline_dict.get(target, "")),
            "chinese": "",
            "example": "",
            "item": {},
            "source": "offline_dict",
        }

    return {
        "word": target,
        "base": target,
        "english": "",
        "chinese": "",
        "example": "",
        "item": {},
        "source": "unresolved",
    }


def is_resolved(word, vocab_items=None, offline_dict=None):
    return bool(resolve_vocab(word, vocab_items, offline_dict).get("english"))
