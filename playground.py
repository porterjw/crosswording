import os, json, pprint, time, random
import textLibrary as txtlib
from openai import OpenAI
from copy import copy as duplicate
from dotenv import load_dotenv
from keybert import KeyBERT

load_dotenv()
client = OpenAI(
        api_key=os.environ.get("OPEN_AI_KEY"),
        )

def keywords(ex_paragraph):
    prompt = txtlib.KEYWORD_EXTRACT.format(paragraph=ex_paragraph)
    keywords = client.chat.completions.create(
        messages=[
                {
                "role": "system",
                "content": prompt,
                }
        ],
        model="gpt-3.5-turbo",
        response_format={ "type": "json_object"}
        )
    print(f"Tokens used in keyword extraction: in:{keywords.usage.prompt_tokens}, out:{keywords.usage.completion_tokens}")
    return json.loads(keywords.choices[0].message.content)['keywords']

def filter_keywords(keywords):
    return [k for k in keywords if (len(k.split()) <= 3)]

def clue_generator(keywords, text):
    prompt = txtlib.CLUE_GENERATOR.format(keywords=keywords, text=text)
    clues = client.chat.completions.create(
        messages=[
                {
                "role": "system",
                "content": prompt,
                }
        ],
        model="gpt-4-turbo",
        response_format={ "type": "json_object"}
        )
    print(f"Tokens used in clue generation: in:{clues.usage.prompt_tokens}, out:{clues.usage.completion_tokens}")
    return json.loads(clues.choices[0].message.content)['clues']

class InvalidWordFit(Exception):
    """Custom exception class for specific error handling."""
    def __init__(self, message):
        super().__init__(message)

class Crossword:
    def __init__(self, cols, rows, empty = '#', available_words=[]):
        self.cols = cols
        self.rows = rows
        self.empty = empty
        self.availalble_words = available_words
        self.current_words = []
        self.board = self.init_board()
        self.wrapWords()

    def wrapWords(self):
        words = []
        for word in self.availalble_words:
            words.append(Word(word))
        self.availalble_words = words

    def init_board(self):
        return [[self.empty for _ in range(self.rows)] for _ in range(self.cols)]

    def print_board(self):
        n = self.rows
        print()
        for i in range(n):
            print(" ".join(self.board[i]))
        print()

    def midpoint(self, n):
        return int(round((n + 1)/2, 0))

    def place_word(self, word):
        # assumes fitting correctly
        row, col = word.row, word.col
        for letter in word.word:
            self.board[row][col] = letter
            if word.vertical:
                row+= 1
            else:
                col+= 1
    

    def check_valid_fit(self, word):
        row, col = word.row, word.col
        for letter in word.word:
            try:
                board_letter = self.board[row][col]
                if board_letter != self.empty and board_letter != letter:
                    return False
                else:
                    if word.vertical:
                        row+= 1
                    else:
                        col+= 1
            except IndexError:
                return False
        return True

    def find_intersections(self, word):
        # I'm sorry about these for loops, but I think this is necessary.
        intersections = []
        for checkword in self.current_words:
            for i, letter in enumerate(word.word):
                for j, check_letter in enumerate(checkword.word):
                    if letter == check_letter:
                        intersections.append([checkword, j, word, i])

        return intersections

    def try_fit(self, intersection):
        placedWord, p_index, newWord, n_index = intersection
        row, col = 0,0
        if placedWord.vertical:
            newWord.row = placedWord.row + p_index
            newWord.col = placedWord.col - n_index
            newWord.vertical = False
        else:
            newWord.row = placedWord.row - n_index
            newWord.col = placedWord.col + p_index
            newWord.vertical = True
        
        if not self.check_valid_fit(newWord):
            raise InvalidWordFit(f"word:{newWord.word} doesn't fit at {newWord.row}, {newWord.col}")

        return newWord
    
    def try_place(self, word):
        n = len(self.board[0])
        if len(self.current_words) == 0:
            vertical, col, row, n = random.randrange(0,2), 0, 0, len(self.board)
            if vertical:
                col = self.midpoint(n)
                row = self.midpoint(n) - self.midpoint(len(word.word))
            else:
                col = self.midpoint(n) - self.midpoint(len(word.word))
                row = self.midpoint(n)

            word.row = row
            word.col = col
            self.current_words.append(word)
            self.place_word(word)
        else:
            intersections = self.find_intersections(word)
            for intersection in intersections:
                try:
                    fittedWord = self.try_fit(intersection)
                    self.place_word(fittedWord)
                except InvalidWordFit as e:
                    print(e)
                    continue
                

    def compute_crossword(self, time_permitted):
        print("computing crosswords now...")
        time_permitted = float(time_permitted)
        copy = duplicate(self)
        start = float(time.time())
        # float(time.time()) - start) > time_permitted
        current_words = []
        for word in copy.availalble_words:
            if word not in copy.current_words:
                print(f'testing {word}')
                copy.try_place(word)
                copy.print_board()
                print(copy.current_words)

class Word:
    def __init__(self, word=None, clue=None):
        self.word = word.lower()
        self.clue = clue
        self.len = len(self.word)
        self.srow = None
        self.scol = None
        self.vertical = None

    def __repr__(self) -> str:
        return self.word
    
def schema_generator(crosswords):
        # { answer: clue }
        answers = sorted(crosswords.keys(), key = len, reverse = True)
        n = len(answers[0])
        cw = Crossword(n, n, available_words=answers)
        cw.compute_crossword(2)

def print_attributes(obj):
    for attr, value in obj.__dict__.items():
        print(f"{attr}: {value}")

if __name__ == "__main__":
#     text = txtlib.SLOTH_CASUAL
#     keywords = filterKeywords(keywords(text))
#     pprint.pprint(keywords)
#     clues = clueGenerator(keywords, text)
#     print(clues)
    with open('crosswords.json', 'r') as file:
        crosswords = json.load(file)
    
    print(crosswords.keys())
    schema_generator(crosswords)

# { SCHEMA EXPECTATION
#   across: {
#     1: {
#       clue: 'one plus one',
#       answer: 'TWO',
#       row: 0,
#       col: 0,
#     },
#   },
#   down: {
#     2: {
#       clue: 'three minus two',
#       answer: 'ONE',
#       row: 0,
#       col: 2,
#     },
#   },
# }