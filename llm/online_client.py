import config

class OnlineClient:
    """
    Client for interacting with online OpenAI-compatible endpoints.
    Allows user-defined API Key and custom base URLs (e.g. Berget.ai).
    """
    def __init__(self, api_key=None, api_base=None, model=None):
        self.api_key = api_key or config.OPENAI_API_KEY
        self.api_base = api_base or config.OPENAI_API_BASE
        self.model = model or config.DEFAULT_ONLINE_MODEL

    def check_connection(self):
        """
        Validates whether API key is provided and formatted correctly.
        """
        try:
            import openai  # noqa: F401
        except ImportError:
            return False, "The OpenAI Python package is not installed. Install project requirements before using Online Mode."

        if not self.api_key or len(self.api_key.strip()) < 5:
            return False, "API Key is empty or invalid. Please check your config or input it in the setup screen."
        
        # We can also do a quick lightweight model listing to check connection if needed
        return True, "API configuration has been loaded successfully."

    def chat_complete(self, messages, temperature=0.7):
        """
        Invokes Chat Completion on the online LLM endpoint.
        """
        is_ok, msg = self.check_connection()
        if not is_ok:
            return f"Error: API Key validation failed.\n\n{msg}"

        try:
            import openai
            # Initialize client with specified base and key
            client = openai.OpenAI(
                api_key=self.api_key,
                base_url=self.api_base
            )
            
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature
            )
            return response.choices[0].message.content
        except openai.AuthenticationError as e:
            return (
                f"Authentication Error: The provided API Key is rejected by {self.api_base}.\n"
                f"Details: {e}\n\n"
                "Please verify your key or try using Berget.ai credits."
            )
        except Exception as e:
            return f"Online API Error: Failed to generate response.\nDetails: {e}"

if __name__ == "__main__":
    cli = OnlineClient(api_key="mock-key")
    print(cli.check_connection())
