import requests
from requests.exceptions import ConnectTimeout
import shutil
from bs4 import BeautifulSoup
from datetime import datetime
import os
from tempfile import gettempdir
import termcolor

URL = "http://feeds.feedblitz.com/korean-word-of-the-day"
DEFAULT_REQUEST_TIMEOUT = 3  # 3 seconds
# URL_FOR_AUDIO = "https://www.transparent.com/word-of-the-day/today/korean.html"  # TODO WIP
# URL_FOR_AUDIO = "https://wotd.transparent.com/widget/?lang=korean&_ga=2.191404842.1871955312.1601750216-1232972085.1601537782"  # TODO WIP

TITLE = f"{termcolor.colored('Korean', 'cyan')} " \
        f"{termcolor.colored('Word', 'yellow')} " \
        f"{termcolor.colored('of', 'green')} " \
        f"{termcolor.colored('the', 'magenta')} " \
        f"{termcolor.colored('Day', 'red')}"
PART_OF_SPEECH = termcolor.colored("Part of speech:", color=None, attrs=["bold"])
EXAMPLE_SENTENCE = termcolor.colored("Example sentence:", color=None, attrs=["bold"])
SENTENCE_MEANING = termcolor.colored("Sentence meaning:", color=None, attrs=["bold"])
LEFT_BRACKET = termcolor.colored("[", color="red", attrs=["bold"])
RIGHT_BRACKET = termcolor.colored("]", color="red", attrs=["bold"])


TIME_FORMAT_FROM_WEB = "%a, %d %b %Y %H:%M:%S %Z"
TIME_FORMAT = "%a, %d %b %Y %H:%M:%S"

BASE_SAVE_PATH = os.path.join(gettempdir(), "korean_word_of_the_day")
PATH_TO_SAVE_TXT = os.path.join(BASE_SAVE_PATH, "korean_word_of_the_day.txt")


def extract_word(raw_content):
    s = raw_content.rindex("<title>")
    e = raw_content.rindex("</title>")
    current = raw_content[s:e]
    return current[current.find("CDATA")+5:-2][1:-1]


def is_still_relevant(now, saved):
    return not(now.day > saved.day or now.month > saved.month or now.year > saved.year)


# def get_audio_links():  # TODO WIP
#     _response = requests.get(URL_FOR_AUDIO)
#     response_content = _response.content.decode()
#     soup = BeautifulSoup(response_content, "lxml")
#     print()


def download():
    global TITLE, URL, DEFAULT_REQUEST_TIMEOUT
    _response = requests.get(URL, timeout=DEFAULT_REQUEST_TIMEOUT)
    response_content = _response.content.decode()

    soup = BeautifulSoup(response_content, "lxml")

    word = extract_word(response_content)
    all_tr = soup.find_all("tr")
    part_of_speech = all_tr[0].text.replace("\n", "").split(":")[1]
    example_sentence = all_tr[1].text.replace("\n", "").split(":")[1]
    sentence_meaning = all_tr[2].text.replace("\n", "").split(":")[1]
    timestamp = datetime.strptime(soup.pubdate.text, "%a, %d %b %Y %H:%M:%S %Z")

    # audio_links = get_audio_links()

    msg = word + "\n" + part_of_speech + "\n" + example_sentence + "\n" + sentence_meaning
    if os.path.exists(PATH_TO_SAVE_TXT):
        os.remove(PATH_TO_SAVE_TXT)
    with open(PATH_TO_SAVE_TXT, 'w') as fp:
        fp.write(str(timestamp.strftime(TIME_FORMAT).strip()) + "\n")
        fp.write(msg)
        fp.write("\n")
    return word, part_of_speech, example_sentence, sentence_meaning


def main():

    try:
        current_ts = datetime.now()
        os.makedirs(BASE_SAVE_PATH, exist_ok=True)
        if os.path.exists(PATH_TO_SAVE_TXT):
            with open(PATH_TO_SAVE_TXT, 'r') as fp:
                timestamp = fp.readline().strip()
                word = fp.readline().strip()
                part_of_speech = fp.readline().strip()
                example_sentence = fp.readline().strip()
                sentence_meaning = fp.readline().strip()
                # word_audio = fp.readline().strip()
                # sentence_audio = fp.readline().strip()
            timestamp = datetime.strptime(timestamp, TIME_FORMAT)
            if is_still_relevant(current_ts, timestamp):
                pass
            else:
                shutil.rmtree(BASE_SAVE_PATH)
                os.makedirs(BASE_SAVE_PATH)
                word, part_of_speech, example_sentence, sentence_meaning = download()
        else:
            word, part_of_speech, example_sentence, sentence_meaning = download()
        print(TITLE)
        print(f"{LEFT_BRACKET}{word}{RIGHT_BRACKET}")
        print(PART_OF_SPEECH, part_of_speech)
        print(EXAMPLE_SENTENCE, example_sentence)
        print(SENTENCE_MEANING, sentence_meaning)
    except ConnectTimeout as e:
        print(TITLE, "Connection Timed Out!")
    except Exception as e:
        print(TITLE, e)



if __name__ == '__main__':
    main()
