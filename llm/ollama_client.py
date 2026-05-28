import requests
import json
import config

class OllamaClient:
    """
    Client for interacting with local Ollama chat completion API.
    Includes active server health checks and model availability diagnostics.
    """
    def __init__(self, endpoint=None, model=None):
        self.endpoint = (endpoint or config.OLLAMA_ENDPOINT).rstrip("/")
        self.model = model or config.DEFAULT_LOCAL_MODEL

    def check_connection(self):
        """
        Pings Ollama server root. Returns tuple (is_running, message).
        """
        try:
            # Ping base endpoint
            resp = requests.get(f"{self.endpoint}/", timeout=2)
            if resp.status_code == 200:
                # Query tags to see what models are pulled
                models = self.get_available_models()
                models_str = ", ".join(models) if models else "None loaded"
                return True, f"Ollama is running! Available models: {models_str}"
            return False, f"Unexpected response status {resp.status_code} from {self.endpoint}"
        except requests.exceptions.RequestException as e:
            return False, (
                f"Ollama server is not detected at {self.endpoint}.\n"
                "Please make sure Ollama is installed and running on your system.\n"
                "To start it in your terminal, run: ollama serve"
            )

    def get_available_models(self):
        """
        Queries /api/tags to list downloaded local models.
        """
        try:
            resp = requests.get(f"{self.endpoint}/api/tags", timeout=2)
            if resp.status_code == 200:
                data = resp.json()
                models = [item["name"] for item in data.get("models", [])]
                # Strip tag suffixes if present, e.g. "qwen2.5:latest" -> "qwen2.5"
                clean_models = []
                for m in models:
                    clean_models.append(m)
                    if ":" in m:
                        clean_models.append(m.split(":")[0])
                return list(set(clean_models))
        except Exception:
            pass
        return []

    def chat_complete(self, messages, temperature=0.7):
        """
        Sends chat completion request to local Ollama.
        """
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature
            }
        }
        
        # Check connection first
        alive, msg = self.check_connection()
        if not alive:
            # Return detailed diagnostic error instructions
            return (
                f"Error: Ollama is offline.\n\n"
                f"{msg}\n\n"
                f"Suggested action: Open your terminal and run:\n"
                f"ollama pull {self.model}\n"
                f"Then verify with: ollama run {self.model}"
            )

        # Pull check
        avail_models = self.get_available_models()
        if self.model not in avail_models and f"{self.model}:latest" not in avail_models:
            print(f"Warning: Selected model '{self.model}' might not be pulled in Ollama. Attempting to run anyway...")

        try:
            url = f"{self.endpoint}/api/chat"
            resp = requests.post(url, json=payload, timeout=20)
            if resp.status_code == 200:
                result = resp.json()
                return result.get("message", {}).get("content", "")
            else:
                return f"Ollama API Error: HTTP Status {resp.status_code} - {resp.text}"
        except requests.exceptions.RequestException as e:
            return f"Ollama Connection Error: Failed to contact Ollama endpoint. Details: {e}"

if __name__ == "__main__":
    cli = OllamaClient()
    is_ok, status_msg = cli.check_connection()
    print(f"Connection OK: {is_ok}\nStatus: {status_msg}")
    
    if is_ok:
        test_messages = [{"role": "user", "content": "Svara med hej på svenska."}]
        print("Response:", cli.chat_complete(test_messages))
