import mss
import numpy as np
import cv2
import time

def capture_region(x, y, width, height):
    """
    Captures a specific region of the screen and returns a NumPy array.
    """
    with mss.mss() as sct:
        # Define the monitor area to capture
        region = {"top": y, "left": x, "width": width, "height": height}
        
        # Grab the data
        sct_img = sct.grab(region)
        
        # Convert to numpy array and drop the alpha channel (BGRA -> BGR)
        img = np.array(sct_img)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        return img

if __name__ == "__main__":
    print("--- Capture Engine Test ---")
    print("Capturing a 400x200 area at (100, 100) in 3 seconds...")
    time.sleep(3) # Give user time to place something interesting at (100, 100)
    
    # Simulate receiving coordinates from the UI Lens
    frame = capture_region(100, 100, 400, 200)
    
    # VERIFIABLE OUTPUT: Save the captured frame to the debug folder
    output_path = "debug_output/capture_test.png"
    cv2.imwrite(output_path, frame)
    
    print(f"Capture complete. Check: {output_path}")
    print(f"Array Shape: {frame.shape} (Height, Width, Channels)")
    print("--- Test Finished ---")