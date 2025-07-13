import keyboard
import difflib

try:
    with open("russian_words.txt", encoding="utf-8") as f:
        russian_words = set(line.strip() for line in f if line.strip())
except FileNotFoundError:
    print("Error: Download the word list and put it in the same folder with the script.")
    exit(1)

translit_map = {
    "sh": "ш", "ch": "ц", "ja": "я", "ju": "ю", "jo": "ё", "zh": "ж",
    "je": "е", "a": "а", "b": "б", "v": "в", "g": "г", "d": "д", "z": "з",
    "i": "и", "k": "к", "l": "л", "m": "м", "n": "н", "o": "о",
    "p": "п", "r": "р", "s": "с", "t": "т", "u": "у", "f": "ф", "h": "х",
    "õ": "ы", "e": "э"
}

buffer = ""

def transliterate(word):
    result = ""
    i = 0
    while i < len(word):
        if i + 1 < len(word) and word[i:i+2] in translit_map:
            result += translit_map[word[i:i+2]]
            i += 2
        elif word[i] in translit_map:
            result += translit_map[word[i]]
            i += 1
        else:
            result += word[i]
            i += 1
    return result

def autocorrect(word):
    if word in russian_words:
        return word
    suggestions = difflib.get_close_matches(word, russian_words, n=1, cutoff=0.8)
    return suggestions[0] if suggestions else word

def capitalize_match(original, corrected):
    if original.isupper():
        return corrected.upper()
    elif original[0].isupper():
        return corrected.capitalize()
    return corrected

def process_buffer(buf):
    if not buf:
        return ""
    lower_buf = buf.lower()
    trans = transliterate(lower_buf)
    corrected = autocorrect(trans)
    return capitalize_match(buf, corrected)

def backspace(count=1):
    for _ in range(count):
        keyboard.write('\b')

print("Starting global Estonian→Russian transliterator with autocorrect.")
print("Press ESC to exit.")

def on_key(event):
    global buffer

    if event.event_type != 'down':
        return

    name = event.name

    if len(name) > 1 and name not in ("space", "backspace", "enter", "esc"):
        return

    if name == "esc":
        print("Exiting...")
        keyboard.unhook_all()
        exit(0)

    if name == "space" or name == "enter":
        if buffer:
            corrected = process_buffer(buffer)
            if corrected != buffer:
                backspace(len(buffer))
                keyboard.write(corrected)
            buffer = ""
        keyboard.write(" " if name == "space" else "\n")
        return False  

    if name == "backspace":
        if buffer:
            buffer = buffer[:-1]
        keyboard.send("backspace")
        return False  

    if len(name) == 1:
        buffer += name
        max_combo_len = 2
        replaced = False

        for length in range(max_combo_len, 0, -1):
            if len(buffer) >= length:
                part = buffer[-length:].lower()
                if part in translit_map:
                    backspace(length)
                    combo = buffer[-length:]
                    cyr = translit_map[part].upper() if combo[0].isupper() else translit_map[part]
                    keyboard.write(cyr)
                    buffer = buffer[:-length]
                    replaced = True
                    break
        if replaced:
            return False  

        if len(buffer) > 20:
            buffer = buffer[-20:]
    else:
        buffer = ""

keyboard.hook(on_key)
keyboard.wait()
