import requests

def translate_text(text, source_lang="auto", target_lang="en"):
    """
    Sends text to the local LibreTranslate server.
    """
    url = "http://127.0.0.1:5000/translate"
    payload = {
        "q": text,
        "source": source_lang,
        "target": target_lang,
        "format": "text"
    }
    
    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            return response.json().get("translatedText")
        else:
            return f"Error: Server returned {response.status_code}"
    except Exception as e:
        return f"Error: Could not connect to LibreTranslate. {e}"

if __name__ == "__main__":
    # Test Logic
    print("--- Local Translation Heartbeat ---")
    test_phrase = "Hola mundo, esto es una prueba local."
    print(f"Original: {test_phrase}")
    
    result = translate_text(test_phrase, source_lang="es", target_lang="en")
    print(f"Translated: {result}")
    print("--- Heartbeat Finished ---")