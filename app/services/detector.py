from typing import Optional
import numpy as np
from keras.models import load_model
import pickle
import joblib
from app.core.config import settings
from datetime import datetime
from keras_preprocessing.sequence import pad_sequences
import re
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords, wordnet
from nltk import pos_tag
from nltk.stem import WordNetLemmatizer
from deep_translator import GoogleTranslator
import time

lemmatizer = WordNetLemmatizer()
model = load_model(settings.MODEL_PATH)
model_temporal = load_model(settings.MODEL_TEMPORAL_PATH)

with open(settings.TOKENIZER_PATH, "rb") as f:
    tokenizer = pickle.load(f)

with open(settings.TEMPORAL_SCALER_PATH, "rb") as f:
    temporal_scaler = joblib.load(f)


def clean_text(text):
    text = re.sub(r"[^a-zA-Z\s]", "", text)

    # Remove extra spaces
    text = re.sub(r"\xa0", " ", text)  # Replace non-breaking space with a regular space
    text = re.sub(r"\s+", " ", text)  # Replace multiple spaces with a single space
    text = re.sub(r"\n", " ", text)
    text = re.sub(r"\r", " ", text)
    text = re.sub(r"\t", " ", text)
    text = text.strip()

    text = re.sub(r"\bUS\b", "United States", text)

    text = text.lower()

    return text


def remove_stop_words(text):
    tokens = word_tokenize(text)
    stop_words = set(stopwords.words("english"))
    tokens = [word for word in tokens if word not in stop_words]

    return " ".join(tokens)


def get_wordnet_pos(tag):
    if tag.startswith("J"):
        return wordnet.ADJ
    elif tag.startswith("V"):
        return wordnet.VERB
    elif tag.startswith("N"):
        return wordnet.NOUN
    elif tag.startswith("R"):
        return wordnet.ADV
    return None


def lemmatize(text):
    lemmatizer = WordNetLemmatizer()
    tokens = word_tokenize(text)
    pos_tags = pos_tag(tokens)
    result = []
    for token, tag in pos_tags:
        wn_tag = get_wordnet_pos(tag)
        if wn_tag is None:
            result.append(token)  # keep original
        else:
            result.append(lemmatizer.lemmatize(token, wn_tag))
    return " ".join(result)


def clean_and_remove_stopwords(text: str) -> str:
    text = clean_text(text)
    text = lemmatize(text)
    text = remove_stop_words(text)
    return text


def tokenize_and_pad(texts):
    sequences = tokenizer.texts_to_sequences(texts)
    padded_sequences = pad_sequences(sequences, padding="post", maxlen=103)
    return padded_sequences


def extract_temporal_features(date: Optional[str]):
    try:
        date = datetime.fromisoformat(date)
        print(date)

        weekday = date.weekday()
        week = date.isocalendar()[1]
        month = date.month
        days_to_election = (datetime(date.year, 11, 5) - date).days

        print(
            f"Extracted temporal features:  {month}, {weekday}, {week}, {days_to_election}"
        )

        temporal_data = temporal_scaler.transform(
            np.array([[weekday, week, month, abs(days_to_election)]])
        )

        print(f"Scaled temporal features: {temporal_data}")

        return temporal_data
    except Exception as e:
        print(f"Error extracting temporal features: {e}")
        return None


def detect_text(headline: str, date: Optional[str]):
    start_time = time.time()

    translator = GoogleTranslator("auto", "en")

    translated_headline = translator.translate(headline)

    clean = clean_and_remove_stopwords(translated_headline)

    X_text = tokenize_and_pad([clean])
    X_temp = extract_temporal_features(date)

    if X_temp is None:
        prob = float(model.predict(X_text, verbose=1)[0][0])
    else:
        prob = float(model_temporal.predict([X_text, X_temp], verbose=1)[0][0])

    duration_ms = (time.time() - start_time) * 1000

    return {
        "detection": prob > 0.5,
        "probability": round(prob if prob > 0.5 else 1 - prob, 4),
        "detection_duration": round(duration_ms, 2),  # in milliseconds
    }
