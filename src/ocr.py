import pytesseract
from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal
from translator import LocalTranslator

class OCRProcessor(QObject):
    data_processed = pyqtSignal(list)
    finished = pyqtSignal()

    def __init__(self, tess_lang, lib_source, lib_target, join_char):
        super().__init__()
        self.tess_lang = tess_lang      # e.g., 'jpn' or 'eng'
        self.lib_source = lib_source    # e.g., 'ja' or 'en'
        self.lib_target = lib_target    # e.g., 'en' or 'es'
        self.join_char = join_char      # "" for Japanese, " " for English
        self.translator = LocalTranslator()

    @pyqtSlot(object)
    def process_frame(self, frame):
        try:
            # 1. Use the specific language selected by the user
            data = pytesseract.image_to_data(frame, output_type=pytesseract.Output.DICT, lang=self.tess_lang)
            
            blocks = {}
            n_boxes = len(data['text'])
            
            for i in range(n_boxes):
                text = data['text'][i].strip()
                try: conf = int(data['conf'][i])
                except ValueError: conf = 0
                
                # Confidence threshold
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

            final_data = []
            for b_id, b_data in blocks.items():
                # 2. Join words using the language-specific separator
                sentence = self.join_char.join(b_data['words'])
                
                final_x = b_data['x_min'] // 2
                final_y = b_data['y_min'] // 2
                final_w = (b_data['x_max'] - b_data['x_min']) // 2
                final_h = (b_data['y_max'] - b_data['y_min']) // 2
                
                # 3. Translate using the specific source/target codes
                translated = self.translator.translate(
                    sentence, 
                    source_lang=self.lib_source, 
                    target_lang=self.lib_target
                )
                
                box_info = {
                    'coords': (final_x, final_y, final_w, final_h),
                    'original': sentence,
                    'translated': translated
                }
                final_data.append(box_info)
                # Debug print to verify correct joining
                print(f"[PIPELINE] '{sentence[:15]}...' -> '{translated[:15]}...'")
            
            self.data_processed.emit(final_data)
                
        except Exception as e:
            print(f"[ERROR] OCR failed: {e}")
        finally:
            self.finished.emit()