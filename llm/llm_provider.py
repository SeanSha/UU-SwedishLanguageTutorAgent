from llm.ollama_client import OllamaClient
from llm.online_client import OnlineClient
import config

class LLMProvider:
    """
    Factory provider that exposes a unified interface, routing requests
    either to OllamaClient (Local Mode) or OnlineClient (Online Mode).
    """
    def __init__(self, mode="Local Mode", ollama_endpoint=None, local_model=None, 
                 online_key=None, online_base=None, online_model=None):
        self.mode = mode
        
        # Instantiate clients with configs
        self.ollama_client = OllamaClient(
            endpoint=ollama_endpoint or config.OLLAMA_ENDPOINT,
            model=local_model or config.DEFAULT_LOCAL_MODEL
        )
        
        self.online_client = OnlineClient(
            api_key=online_key or config.OPENAI_API_KEY,
            api_base=online_base or config.OPENAI_API_BASE,
            model=online_model or config.DEFAULT_ONLINE_MODEL
        )

    def check_connection(self):
        """
        Executes connection check based on active mode.
        """
        if self.mode == "Local Mode":
            return self.ollama_client.check_connection()
        else:
            return self.online_client.check_connection()

    def chat_complete(self, messages, temperature=0.7):
        """
        Routes the chat completion query to the active client.
        """
        if self.mode == "Local Mode":
            return self.ollama_client.chat_complete(messages, temperature=temperature)
        else:
            return self.online_client.chat_complete(messages, temperature=temperature)

if __name__ == "__main__":
    prov = LLMProvider(mode="Local Mode")
    print("Local Mode check:", prov.check_connection())
