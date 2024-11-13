import re
import requests

from bs4 import BeautifulSoup


DEFINITION_URL = "https://dictionary.cambridge.org/dictionary/english/"
REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:106.0) Gecko/20100101 Firefox/106.0",
    "Accept-Language": "en-US,en;q=0.5",
}


def decode_escaped_chars(strg):
    return strg.encode("utf8").decode("utf8", "strict")


# [SOURCE]: https://github.com/rocktimsaikia/cambd/blob/main/cambd/cambd.py
def get_definitions(word: str):
    response = requests.get(DEFINITION_URL + word, headers=REQUEST_HEADERS)

    # We are considering a word to be invalid based on redirection only but that may not be the case for valids words
    # with spcaes which we are handling it above statement
    if (
        response.history
        and response.history[0].status_code == 302
        and response.url == "https://dictionary.cambridge.org/dictionary/english/"
    ):
        return []

    soup = BeautifulSoup(response.content, "html5lib")
    definitions = []

    dictionaries = soup.find_all(attrs={"class": "dictionary"})
    for dictionary in dictionaries:
        def_blocks = dictionary.find_all(attrs={"class": "ddef_block"})
        dict_region = dictionary.find(attrs={"class": "region"}).get_text().upper()

        ipa = ''
        us_ipa = soup.find(attrs={"class": "us"}).get_text()
        if us_ipa:
            ipa = soup.find(attrs={"class": "ipa"}).get_text()

        for dblock in def_blocks:
            word_type = dblock.find(attrs={"class": "dsense_pos"})
            # use parent's if local not defined
            if word_type == None:
                word_type = dictionary.find(attrs={"class": "dpos"})
            word_type = word_type.get_text() if word_type is not None else None

            # Info about word codes and lables (https://dictionary.cambridge.org/help/codes.html)
            def_info = dblock.find(attrs={"class": "def-info"})
            def_info = def_info.get_text().strip() if def_info is not None else None

            definition = dblock.find(attrs={"class": "ddef_d"})
            if definition:
                definition = dblock.find(attrs={"class": "ddef_d"}).get_text()
                example_containers = dblock.find_all(attrs={"class": "examp"})
                examples = []

                for expl in example_containers:
                    example_text = expl.get_text().strip()
                    example_text = decode_escaped_chars(example_text)
                    examples.append('-' + example_text)

                definition = definition.strip().capitalize()
                definition = definition[:-1] if definition.endswith(":") else definition
                definition = str(re.sub("[ \n]+", " ", definition))

                if len(examples) > 2:
                    examples = examples[:2]

                definition_dict = {
                    "word": word,
                    "ipa": ipa,
                    "definition": definition,
                    "type": word_type,
                    "dictionaryRegion": dict_region,
                    "info": def_info,
                    "examples": examples,
                }
                definitions.append(definition_dict)

    return definitions

