import os
from translator import translate_text

def process_and_translate(ocr_results, target_lang="en"):
    """
    Takes OCR results, cleans them, translates, and returns 
    a list of dictionaries ready for the UI overlay.
    """
    final_translations = []

    print(f"--- Translating {len(ocr_results)} blocks ---")

    for item in ocr_results:
        original_text = item['text']
        
        # 1. CLEANING: Remove newlines and extra spaces 
        # (Crucial for Japanese vertical text and split English sentences)
        cleaned_text = original_text.replace('\n', ' ').strip()
        
        if len(cleaned_text) < 1:
            continue

        # 2. TRANSLATE: Hit the local LibreTranslate server
        # Note: 'auto' allows the server to detect if it's jpn or eng
        translated_text = translate_text(cleaned_text, source_lang="auto", target_lang=target_lang)
        
        # 3. MAPPING: Store the translation with its original box
        final_translations.append({
            "box": item['box'],
            "original": cleaned_text,
            "translated": translated_text
        })
        
        # VERIFIABLE OUTPUT: Print the mapping
        print(f"Mapped Box {item['box']}:")
        print(f"  In:  {cleaned_text[:50]}...")
        print(f"  Out: {translated_text}")

    return final_translations

if __name__ == "__main__":
    # Simulate a run using the outputs from your previous OCR step
    # We will use one of your successful OCR outputs for this test
    mock_ocr_results = [
        {"box": [0, 97, 334, 132], "text": "元来日本語は漢文に父い、文字を上\nから下へ、また行を右から左へと進\nめて表記を行っていた。"},
        {"box": [362, 18, 28, 86], "text": "横\n書\nき\n不"}
    ]
    
    # Ensure LibreTranslate is running in the background!
    results = process_and_translate(mock_ocr_results)
    
    print("\n--- Final Translation Bridge Test Complete ---")