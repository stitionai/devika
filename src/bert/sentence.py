from keybert import KeyBERT

class SentenceBert:
    def __init__(self, sentence: str):
        self.sentence = sentence
        self.kw_model = KeyBERT()

    def extract_keywords(self, top_n: int = 5) -> list:
        keywords = self.kw_model.extract_keywords(
            self.sentence,
            keyphrase_ngram_range=(1, 1),
            stop_words='english',
            top_n=top_n,
            use_mmr=True,
            diversity=0.7
        )
        return keywords
