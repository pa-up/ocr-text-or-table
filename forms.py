import numpy as np


asprise_ocr_language_options = np.array([
    ["English", "eng"],
    ["Spanish", "spa"],
    ["Portuguese", "por"],
    ["German", "deu"],
    ["French", "fra"],
])

google_translate_language_options = np.array([
    ["auto", "auto"],
    ["Japanese", "ja"],
    ["English", "en"],
    ["Spanish", "es"],
    ["Portuguese", "pt"],
    ["German", "de"],
    ["French", "fr"],
    ["Italian", "it"],
    ["Russian", "ru"],
    ["Arabic", "ar"],
    ["Turkish", "tr"],
    ["Korean", "ko"],
    ["Chinese (Simplified)", "zh-CN"],
    ["Chinese (Traditional)", "zh-TW"],
    ["Hindi", "hi"],
    ["Bengali", "bn"],
    ["Ukrainian", "uk"],
    ["Greek", "el"],
    ["Dutch", "nl"],
    ["Czech", "cs"],
    ["Polish", "pl"],
    ["Thai", "th"],
    ["Swedish", "sv"],
    ["Romanian", "ro"],
    ["Finnish", "fi"],
    ["Norwegian", "no"],
    ["Danish", "da"],
    ["Croatian", "hr"],
    ["Indonesian", "id"],
    ["Filipino", "tl"],
    ["Vietnamese", "vi"]
])

drive_ocr_language_options = google_translate_language_options[1 : , :]