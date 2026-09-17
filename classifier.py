import re
from database import get_forms, get_topics


# Các Form mà hệ thống tự nhận diện.
FORM_RULES = [
    ("what", "What", r"^what\b"),
    ("when", "When", r"^when\b"),
    ("where", "Where", r"^where\b"),
    ("why", "Why", r"^why\b"),
    ("who", "Who", r"^who\b"),
    ("how", "How", r"^how\b"),
    ("do", "Do / Does / Did", r"^(do|does|did)\b"),
    ("is", "Is / Are / Was / Were", r"^(is|are|was|were)\b"),
    ("can", "Can / Could", r"^(can|could)\b"),
    ("have", "Have / Has", r"^(have|has)\b"),
    ("would", "Would", r"^would\b"),
    ("tell", "Tell Me About", r"^tell\s+me\s+about\b"),
    ("describe", "Describe", r"^describe\b"),
]


TOPIC_KEYWORDS = {
    "Family": [
        "family", "mother", "father", "parents", "brother",
        "sister", "husband", "wife", "children", "relative"
    ],
    "Travel": [
        "travel", "trip", "tour", "tourist", "holiday", "vacation",
        "visit", "hotel", "airport", "destination", "journey", "beach"
    ],
    "Food": [
        "food", "eat", "meal", "restaurant", "dish", "cook",
        "cooking", "breakfast", "lunch", "dinner", "fruit"
    ],
    "Education": [
        "school", "student", "study", "studying", "teacher",
        "university", "college", "class", "subject", "education",
        "exam", "homework", "english", "learn"
    ],
    "Work": [
        "work", "job", "career", "office", "company",
        "employee", "boss", "profession"
    ],
    "Free Time": [
        "hobby", "hobbies", "free time", "spare time",
        "weekend", "read", "reading", "game", "gaming",
        "exercise", "sport", "music", "movie", "movies"
    ],
    "Hometown": [
        "hometown", "home town", "where do you live",
        "city", "town", "village", "neighborhood", "neighbourhood"
    ],
    "Technology": [
        "technology", "computer", "phone", "smartphone",
        "internet", "social media", "website", "app", "application"
    ],
    "Shopping": [
        "shopping", "shop", "buy", "buying", "store",
        "market", "clothes", "clothing"
    ],
    "Weather": [
        "weather", "rain", "rainy", "sunny", "hot", "cold",
        "season", "summer", "winter"
    ],
}


def find_id_by_name(rows, name):
    for row in rows:
        if row["name"].lower() == name.lower():
            return row["id"]
    return None


def classify_form(question):
    text = question.strip().lower()

    for _, form_name, pattern in FORM_RULES:
        if re.search(pattern, text):
            return form_name

    return "Other"


def classify_topic(question):
    text = question.lower()
    scores = {}

    for topic, keywords in TOPIC_KEYWORDS.items():
        score = sum(1 for keyword in keywords if keyword.lower() in text)
        if score:
            scores[topic] = score

    if not scores:
        return "Other"

    return max(scores, key=scores.get)


def classify_question(question):
    forms = get_forms()
    topics = get_topics()

    form_name = classify_form(question)
    topic_name = classify_topic(question)

    form_id = find_id_by_name(forms, form_name)
    topic_id = find_id_by_name(topics, topic_name)

    # Nếu người dùng đã tạo/xóa tên nào đó khiến classifier không tìm thấy,
    # dùng Other làm dự phòng.
    if form_id is None:
        form_id = find_id_by_name(forms, "Other")

    if topic_id is None:
        topic_id = find_id_by_name(topics, "Other")

    return {
        "form_id": form_id,
        "topic_id": topic_id,
        "form": form_name,
        "topic": topic_name,
    }
