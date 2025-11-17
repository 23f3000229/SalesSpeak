import speech_recognition as sr
from src.utils.logger import get_logger

logger = get_logger(__name__)


def process_speech_to_text(audio_bytes):
    """Convert raw audio bytes to text using Google's recognizer.

    Expects audio_bytes from `audiorecorder.export().read()`.
    Returns recognized text or None on failure.
    """
    recognizer = sr.Recognizer()
    try:
        audio_data = sr.AudioData(audio_bytes, 44100, 2)
        text = recognizer.recognize_google(audio_data)
        return text
    except Exception as e:
        logger.warning(f"Speech recognition failed: {e}")
        return None


def parse_sales_speech(text: str):
    """Parse spoken text into a simple sales structure.

    This is a lightweight parser: first number => quantity, second => price,
    remaining non-numeric words => item name.
    """
    if not text:
        return {'item_name': '', 'quantity': 1, 'price': 0}

    words = text.lower().split()
    parsed_data = {'item_name': '', 'quantity': 1, 'price': 0}
    numbers = [word for word in words if word.replace('.', '').isdigit()]
    if len(numbers) >= 1:
        try:
            parsed_data['quantity'] = float(numbers[0])
        except Exception:
            parsed_data['quantity'] = 1
    if len(numbers) >= 2:
        try:
            parsed_data['price'] = float(numbers[1])
        except Exception:
            parsed_data['price'] = 0

    item_words = [w for w in words if not w.replace('.', '').isdigit() and w not in ['quantity', 'price', 'rupees', 'rs']]
    parsed_data['item_name'] = ' '.join(item_words)
    return parsed_data
