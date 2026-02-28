import requests

class LocalTranslator:
    def __init__(self, host="http://127.0.0.1:5000"):
        self.host = host
        self.cache = {}

    def translate(self, text, source_lang="ja", target_lang="en"):
        if not text.strip():
            return ""
        
        # 1. Check if we have already translated this exact string
        if text in self.cache:
            return self.cache[text]
        
        try:
            # 2. If not in cache, send to local LibreTranslate
            url = f"{self.host}/translate"
            payload = {
                "q": text,
                "source": source_lang,
                "target": target_lang,
                "format": "text"
            }
            headers = {"Content-Type": "application/json"}
            
            # Timeout ensures the UI thread doesn't hang if the server is slow
            response = requests.post(url, json=payload, headers=headers, timeout=2)
            response.raise_for_status()
            
            translated_text = response.json().get("translatedText", "")
            
            # 3. Save to cache for future frames
            self.cache[text] = translated_text
            return translated_text
            
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] LibreTranslate request failed: {e}")
            return text  # Fallback to returning original text if translation fails