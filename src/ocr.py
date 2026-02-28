import pytesseract
from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal
from translator import LocalTranslator

class OCRProcessor(QObject):
    # NEW: Signal to send the final structured data back to the UI thread
    data_processed = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.is_processing = False
        self.translator = LocalTranslator() # Initialize our cached translator

    @pyqtSlot(object)
    def process_frame(self, frame):
        if self.is_processing:
            return
        self.is_processing = True
        
        try:
            # Using your updated lang='jpn'
            data = pytesseract.image_to_data(frame, output_type=pytesseract.Output.DICT, lang='jpn')
            blocks = {}
            n_boxes = len(data['text'])
            
            for i in range(n_boxes):
                text = data['text'][i].strip()
                try: conf = int(data['conf'][i])
                except ValueError: conf = 0
                
                if text and conf > 30:
                    block_id = (data['block_num'][i], data['par_num'][i], data['line_num'][i])
                    x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                    
                    if block_id not in blocks:
                        blocks[block_id] = {'words': [text], 'x_min': x, 'y_min': y, 'x_max': x+w, 'y_max': y+h}
                    else:
                        blocks[block_id]['words'].append(text)
                        blocks[block_id]['x_min'] = min(blocks[block_id]['x_min'], x)
                        blocks[block_id]['y_min'] = min(blocks[block_id]['y_min'], y)
                        blocks[block_id]['x_max'] = max(blocks[block_id]['x_max'], x+w)
                        blocks[block_id]['y_max'] = max(blocks[block_id]['y_max'], y+h)

            final_data =[]
            for b_id, b_data in blocks.items():
                # Join without spaces for Japanese
                sentence = "".join(b_data['words'])
                
                final_x = b_data['x_min'] // 2
                final_y = b_data['y_min'] // 2
                final_w = (b_data['x_max'] - b_data['x_min']) // 2
                final_h = (b_data['y_max'] - b_data['y_min']) // 2
                
                # TRANSLATE THE SENTENCE
                translated = self.translator.translate(sentence, source_lang="ja", target_lang="en")
                
                # Package everything neatly
                box_info = {
                    'coords': (final_x, final_y, final_w, final_h),
                    'original': sentence,
                    'translated': translated
                }
                final_data.append(box_info)
                
                print(f"[PIPELINE] Original: '{sentence[:15]}...' -> Translated: '{translated[:20]}...'")
            
            # Emit the fully processed list
            self.data_processed.emit(final_data)
                
        except Exception as e:
            print(f"[ERROR] OCR/Translation pipeline failed: {e}")
        finally:
            self.is_processing = False