def convert_message_to_dict(text):
    if "#" not in text: return None
    list_row = text.replace("#", "").replace("**", "").split("\n\n")
    return({
        "word": list_row[0],
        "meaning": list_row[1],
        "example": None if len(list_row) < 3 else list_row[2],
    })
    

def get_message_md(word, ipa, definition, example):
    underscore = "\_"

    text = ""
    text += f"#{word.replace(' ', underscore)}\n\n**{word} \[{ipa}\]**: "
    text += f"{definition}\n\n{example}"

    return text