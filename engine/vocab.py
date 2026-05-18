from utils.helper import *

class Vocabulary:
    def __init__(
            self,
            word: str = None,
            ipa: str = None,
            word_type: str = None,
            definition: str = None,
            examples: list[str] | None = None
        ):
        self.word = word
        self.ipa = ipa
        self.examples = examples or []
        self.word_type = word_type
        self.definition = definition

    def init_from_markdown(self, md: str) -> bool:
        if "#" not in md:
            return False

        text = md.replace("**", "")
        list_row = [row.strip() for row in text.split("\n\n") if row.strip()]
        if len(list_row) < 3:
            return False

        word_lines = [line.strip() for line in list_row[0].splitlines() if line.strip()]
        if not word_lines:
            return False

        self.word = word_lines[0].lstrip("#").replace("_", " ").strip()
        if not self.word:
            return False

        self.ipa = None
        if len(word_lines) > 1:
            self.ipa = word_lines[1].replace("[", "").replace("]", "").strip() or None

        self.word_type = list_row[1].replace("__", "").strip()
        self.definition = list_row[2].strip()
        if not self.word_type or not self.definition:
            return False

        self.examples = []
        for block in list_row[3:]:
            for line in block.splitlines():
                cleaned_line = line.strip()
                if not cleaned_line:
                    continue
                self.examples.append(cleaned_line.replace("- ", "", 1))

        return True

    def convert_to_markdown(self, with_hashtag: bool = True, with_spoilers: bool = False) -> str:
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

        md += "**" + ("[" if with_spoilers else "") + self.definition + ("](spoiler)" if with_spoilers else "") + "**"
        md += "\n\n"
        
        if self.examples:
            md += "\n".join([f"- {e}" for e in self.examples])

        return md
