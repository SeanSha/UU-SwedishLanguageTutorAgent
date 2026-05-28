import os
import hashlib
import config

class TTSAvatarTool:
    """
    Generates Swedish Text-To-Speech audio files using gTTS
    and resolves avatar state transitions (neutral, speaking, happy, thinking, correcting)
    to physical image assets in the assets/ folder.
    """
    def __init__(self):
        self.assets_dir = config.ASSETS_DIR
        os.makedirs(self.assets_dir, exist_ok=True)

    def get_cached_tts(self, text):
        """
        Generates or retrieves a cached Swedish gTTS audio path for a given text string.
        Saves files named by the MD5 hash of the text under assets/tts_cache/.
        """
        text = (text or "").strip()
        if not text:
            return None

        text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
        cache_dir = os.path.join(self.assets_dir, "tts_cache")
        os.makedirs(cache_dir, exist_ok=True)
        file_path = os.path.join(cache_dir, f"{text_hash}.mp3")
        
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            return file_path
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError:
                return None
            
        try:
            from gtts import gTTS
            tts = gTTS(text=text, lang='sv')
            tts.save(file_path)
            if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                return file_path
            if os.path.exists(file_path):
                os.remove(file_path)
            return None
        except Exception as e:
            if os.path.exists(file_path) and os.path.getsize(file_path) == 0:
                try:
                    os.remove(file_path)
                except OSError:
                    pass
            print(f"gTTS cache failed for '{text}': {e}")
            return None

    def synthesize_swedish(self, text):
        """
        Synthesizes the given text using Google Translate TTS (Swedish)
        and saves it under a stable per-sentence cache filename.
        Returns the absolute filepath to be loaded by Gradio.
        """
        return self.get_cached_tts(text)

    def get_avatar_image(self, state):
        """
        Resolves the image file path based on avatar state:
        neutral, speaking, happy, thinking, correcting.
        If the physical file does not exist, returns None (Gradio will render a fallback or label).
        """
        valid_states = ["neutral", "speaking", "happy", "thinking", "correcting"]
        if state not in valid_states:
            state = "neutral"

        image_path = os.path.join(self.assets_dir, f"avatar_{state}.png")
        if os.path.exists(image_path):
            return image_path
            
        # Debug fallback indicator
        return None

    def get_avatar_emoji(self, state):
        """
        Fallback textual emoji representation of the avatar state for robust UI display.
        """
        emojis = {
            "neutral": "😐 [Sven - Ready]",
            "speaking": "🗣️ [Sven - Speaking Swedish]",
            "happy": "😊 [Sven - Excellent work!]",
            "thinking": "🤔 [Sven - Let's review...]",
            "correcting": "❌ [Sven - Ah, look at this error]"
        }
        return emojis.get(state, emojis["neutral"])

if __name__ == "__main__":
    tool = TTSAvatarTool()
    path = tool.synthesize_swedish("Hej, hur mår du?")
    print("TTS path:", path)
    print("Avatar path for 'happy':", tool.get_avatar_image("happy"))
