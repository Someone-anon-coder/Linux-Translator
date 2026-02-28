import pytesseract
from PyQt6.QtCore import QObject, pyqtSlot

class OCRProcessor(QObject):
    def __init__(self):
        super().__init__()
        # Lock to prevent stacking OCR tasks if the capture thread sends frames too quickly
        self.is_processing = False

    @pyqtSlot(object)
    def process_frame(self, frame):
        # If we are already running OCR, ignore the new frame to save CPU
        if self.is_processing:
            return
            
        self.is_processing = True
        
        try:
            # 1. Run Tesseract to extract data dictionaries (includes text, conf, and coords)
            data = pytesseract.image_to_data(frame, output_type=pytesseract.Output.DICT)
            
            blocks = {}
            n_boxes = len(data['text'])
            
            # 2. Iterate through all detected items
            for i in range(n_boxes):
                text = data['text'][i].strip()
                # Tesseract occasionally returns empty strings or low confidence noise
                try:
                    conf = int(data['conf'][i])
                except ValueError:
                    conf = 0
                
                if text and conf > 30:
                    # 3. Create a unique ID for the sentence based on layout hierarchy
                    block_id = (data['block_num'][i], data['par_num'][i], data['line_num'][i])
                    
                    x = data['left'][i]
                    y = data['top'][i]
                    w = data['width'][i]
                    h = data['height'][i]
                    
                    # 4. Group words into the same sentence block and expand the bounding box
                    if block_id not in blocks:
                        blocks[block_id] = {
                            'words': [text],
                            'x_min': x,
                            'y_min': y,
                            'x_max': x + w,
                            'y_max': y + h
                        }
                    else:
                        blocks[block_id]['words'].append(text)
                        blocks[block_id]['x_min'] = min(blocks[block_id]['x_min'], x)
                        blocks[block_id]['y_min'] = min(blocks[block_id]['y_min'], y)
                        blocks[block_id]['x_max'] = max(blocks[block_id]['x_max'], x + w)
                        blocks[block_id]['y_max'] = max(blocks[block_id]['y_max'], y + h)

            # 5. Process the grouped blocks
            for b_id, b_data in blocks.items():
                sentence = " ".join(b_data['words'])
                
                # 6. CRITICAL: Divide coordinates by 2 to map back to the UI!
                # (Because we used cv2.resize(fx=2, fy=2) in capture.py)
                final_x = b_data['x_min'] // 2
                final_y = b_data['y_min'] // 2
                final_w = (b_data['x_max'] - b_data['x_min']) // 2
                final_h = (b_data['y_max'] - b_data['y_min']) // 2
                
                # 7. Print the grouped sentence and its relative UI coordinates
                print(f"[OCR DETECTED] Context: '{sentence}' | Coords: X:{final_x:04d} Y:{final_y:04d} W:{final_w:04d} H:{final_h:04d}")
                
        except Exception as e:
            print(f"[ERROR] OCR processing failed: {e}")
        finally:
            # Release the lock so the next frame can be processed
            self.is_processing = False