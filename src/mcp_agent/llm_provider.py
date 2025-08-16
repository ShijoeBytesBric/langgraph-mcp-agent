from langchain.chat_models import init_chat_model
from .config import LLM_CONFIG


class LLMProvider:
    def __init__(self):
        self.model = self.initialize_model()

    def initialize_model(self):
        return init_chat_model(**LLM_CONFIG)
