import pytesseract
from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal
from translator import LocalTranslator

class OCRProcessor(QObject):
    data_processed = pyqtSignal(list)
    finished = pyqtSignal() # NEW: Signal to say "I'm ready for the next frame"

    def __init__(self):
        super().__init__()
        self.translator = LocalTranslator()

    @pyqtSlot(object)
    def process_frame(self, frame):
        try:
            # lang='jpn' for Japanese, or 'eng' for English depending on your test
            data = pytesseract.image_to_data(frame, output_type=pytesseract.Output.DICT, lang='eng+jpn')
            
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

            final_data = []
            for b_id, b_data in blocks.items():
                # Use " " for English, "" for Japanese. 
                # Ideally, detect language or just use " " as a generic separator
                sentence = " ".join(b_data['words'])
                
                final_x = b_data['x_min'] // 2
                final_y = b_data['y_min'] // 2
                final_w = (b_data['x_max'] - b_data['x_min']) // 2
                final_h = (b_data['y_max'] - b_data['y_min']) // 2
                
                translated = self.translator.translate(sentence, source_lang="auto", target_lang="en")
                
                box_info = {
                    'coords': (final_x, final_y, final_w, final_h),
                    'original': sentence,
                    'translated': translated
                }
                final_data.append(box_info)
                print(f"[PIPELINE] '{sentence[:10]}...' -> '{translated[:10]}...'")
            
            self.data_processed.emit(final_data)
                
        except Exception as e:
            print(f"[ERROR] OCR failed: {e}")
        finally:
            # ALWAYS tell the capture thread we are done
            self.finished.emit()