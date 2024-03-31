"""Keyword extraction using BERT."""

# pylint: disable=too-few-public-methods

from typing import List, Tuple

from keybert import KeyBERT


class SentenceBert:
    def __init__(self):
        self.kw_model = KeyBERT()

    def extract_keywords(
        self, sentence: str, top_n: int = 5
    ) -> List[Tuple[str, float]]:

        if isinstance(sentence, list):
            sentence = " ".join(sentence)

        keywords = self.kw_model.extract_keywords(
            sentence,
            keyphrase_ngram_range=(1, 1),
            stop_words="english",
            top_n=top_n,
            use_mmr=True,
            diversity=0.7,
        )
        return keywords
