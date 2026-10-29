import os
import sys

MODEL_PATH = os.path.join(os.path.dirname(__file__), "Eheart_sound_by_Ahsan_Mandhar.onnx")
EXPECTED_SIZE = 87085683

def main():
    if os.path.exists(MODEL_PATH):
        size = os.path.getsize(MODEL_PATH)
        if size == EXPECTED_SIZE:
            print(f"Model already present ({size} bytes).")
            return
        print(f"Existing model size {size} != {EXPECTED_SIZE}; please re-extract the zip.")
        sys.exit(1)
    else:
        print("Model file not found.")
        print("Please ensure you extracted the full zip, including:")
        print("  Eheart_sound_by_Ahsan_Mandhar.onnx")
        sys.exit(1)

if __name__ == "__main__":
    main()
