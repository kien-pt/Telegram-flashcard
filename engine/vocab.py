from utils.helper import *

class Vocabulary:
    def __init__(
            self,
            word: str = None,
            ipa: str = None,
            word_type: str = None,
            definition: str = None,
            examples: list[str] = []
        ):
        self.word = word
        self.ipa = ipa
        self.examples = examples
        self.word_type = word_type
        self.definition = definition

    def init_from_markdown(self, md: str) -> bool:
        if "#" not in md: return False

        text = md.replace("#", "").replace("**", "")
        list_row = text.split("\n\n")

        word_text = list_row[0]
        self.word = word_text.split('\n')[0].replace("_", " ")

        if len(word_text.split('\n')) > 1:
            self.ipa = word_text.split('\n')[1].replace("[ ", "").replace(" ]", "")

        self.word_type = list_row[1].replace("__", "")
        self.definition = list_row[2]

        if len(list_row) > 3:
            self.examples = [w.replace("- ", "") for w in list_row[3].split("\n")]

        return True

    def convert_to_markdown(self, with_hashtag: bool = True) -> str:
        md = ""
        if with_hashtag: md += "#"

        md += normalize_text(self.word)
        md += "\n"

        if self.ipa:
            md += "[" + self.ipa.replace(".", ".\u200b") + "]"
            md += "\n\n"
        else:
            md += "\n"

        md += "__" + self.word_type + "__"
        md += "\n\n"

        md += "**" + self.definition + "**"
        md += "\n\n"
        
        if self.examples:
            md += "\n".join([f"- {e}" for e in self.examples])

        return md
