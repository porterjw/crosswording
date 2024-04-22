import os, json, pprint, time, random
import textLibrary as txtlib
from openai import OpenAI
from copy import deepcopy as duplicate
from dotenv import load_dotenv

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

def add_tuples(t1, t2):
       return tuple(map(lambda i, j: i + j, t1, t2))

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
    def __init__(self, cols, rows, gamedata, empty = '#', available_words=[]):
        self.cols = cols
        self.rows = rows
        self.empty = empty
        self.gamedata = gamedata # this should be by reference conceptually.
        self.available_words = available_words
        self.current_words = []
        self.linked_letters_count = 0
        self.board = self.init_board()
        self.wrapWords()

    def wrapWords(self):
        words = []
        for word in self.available_words:
            words.append(Word(word, clue=self.gamedata[word]))
        self.available_words = words

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

    def place_word(self, word, intersection = None):
        # assumes fitting correctly
        # also appends to the boards current words
        row, col = word.row, word.col
        for letter in word.word:
            self.board[row][col] = letter
            if word.vertical:
                row+= 1
            else:
                col+= 1
        self.current_words.append(word)
        if intersection:
            self.record_intersection(intersection)


    def check_cell_empty(self, pos):
        return self.check_cell_inbounds(pos) and self.board[pos[0]][pos[1]] == self.empty

    def check_cell_inbounds(self, pos):
        row, col = pos
        if row < 0 or col < 0 or row >= self.rows or col >= self.cols:
            return False
        return True

    def check_valid_fit(self, word):
        row, col = word.row, word.col
        for letter in word.word:
            pos = (row, col)
            if not self.check_cell_inbounds(pos):
                return False
            board_letter = self.board[row][col]
            if board_letter != self.empty and board_letter != letter:
                return False
            else:
                if word.vertical:
                    row+= 1
                else:
                    col+= 1
        return True

    def check_valid_neighbor_cell(self, word, neighbor):
        intersections = word.valid_intersections
        for coords in intersections:
            if word.vertical:
                if coords[0] != neighbor[0]:
                    return False # the idea is to compare rows, if the non empty neighbor isn't in row of intersection invalid fit.
            else:
                if coords[1] != neighbor[1]:
                    return False
        return True
    
    def check_crowded_bookends(self, word):
        first, last = 0, 0 # top and bottom or left and right of a word.
        if word.vertical:
            first = (word.row - 1, word.col)
            last = (word.row + len(word.word), word.col)
        else:
            first = (word.row, word.col - 1)
            last = (word.row, word.col + len(word.word))

        # if self.check_cell_inbounds(first) and self.check_cell_inbounds(last) \
        #     and self.check_cell_empty(first) and self.check_cell_empty(last):
        if (self.check_cell_inbounds(first) and not self.check_cell_empty(first)) or \
                (self.check_cell_inbounds(last) and self.check_cell_empty(last)): 
            return True
        return False

    def check_surrounded_fit(self, word):
        neighbors = word.get_surrounding_cells()
        filtered_neighbors = [cell for cell in neighbors if self.check_cell_inbounds(cell)]
        for neighbor in filtered_neighbors:
            if not self.check_cell_empty(neighbor) and not self.check_valid_neighbor_cell(word, neighbor):
                return True
        return False


    def check_crowded_fit(self, word):
        """
        a crowded fit is if two words lay adjacent to one another 
        in the same orientation, i.e.
        ##octopus## 
        ####cat####
        """
        s1, s2 = (word.row, word.col), (word.row, word.col) # create cells to slide along word and check for adjacent neighbors
        if word.vertical:
            s1, s2 = (word.row, word.col-1), (word.row, word.col+1) # shift rows to be on either side of word, shifting col to start one ahead.  
        else:
            s1, s2 = (word.row-1, word.col), (word.row+1, word.col)

        for i in range(len(word.word) - 1):
            if word.vertical:
                slider = (1, 0) 
            else:
                slider = (0, 1)
            # slide our windows one step ahead, to compare to previous for adjacent non-empty cells.
            slid_s1, slid_s2 = add_tuples(s1, slider), add_tuples(s2, slider)
            # compare one slider for adjacent non-empty cells.
            if not self.check_cell_empty(slid_s1) and not self.check_cell_empty(s1):
                return True 
            # check the other slider.
            if not self.check_cell_empty(slid_s2) and not self.check_cell_empty(s2):
                return True
            
            s1, s2 = slid_s1, slid_s2
        return False

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
        if placedWord.vertical:
            newWord.row = placedWord.row + p_index
            newWord.col = placedWord.col - n_index
            newWord.vertical = False
        else:
            newWord.row = placedWord.row - n_index
            newWord.col = placedWord.col + p_index
            newWord.vertical = True
        
        self.record_intersection(intersection)
        
        if not self.check_valid_fit(newWord) or self.check_crowded_fit(newWord) or self.check_surrounded_fit(newWord):
            placedWord.valid_intersections.pop()
            newWord.valid_intersections.pop()
            self.linked_letters_count -= 1
            raise InvalidWordFit(f"word:{newWord.word} doesn't fit at {newWord.row}, {newWord.col} tried with {placedWord.word}, v={newWord.vertical}")
        
        # print(f'Word: {newWord.word} does fit @ {newWord.row}, {newWord.col}.')
        return newWord
    
    def try_place(self, word):
        n = len(self.board[0])
        if len(self.current_words) == 0:
            # random.randrange(0,2)
            vertical, col, row, n = random.randrange(0,2), 0, 0, len(self.board)
            if vertical:
                # col = self.midpoint(n)
                col = random.randrange(0,n-1)
                row = self.midpoint(n) - self.midpoint(len(word.word))
            else:
                col = self.midpoint(n) - self.midpoint(len(word.word))
                # row = self.midpoint(n)
                row = random.randrange(0, n-1)

            word.row = row
            word.col = col
            word.vertical = vertical
            self.place_word(word)
        else:
            intersections = self.find_intersections(word)
            for intersection in intersections:
                try:
                    fittedWord = self.try_fit(intersection)
                    self.place_word(fittedWord, intersection=intersection) # places and appends word to board and current words.
                    break
                except InvalidWordFit as e:
                    # print(e)
                    continue
    
    def record_intersection(self, intersection):
        placedWord, p_index, newWord, n_index = intersection
        if placedWord.vertical:
            coords = (newWord.row, placedWord.col)
        else:
            coords = (placedWord.row, newWord.col)
        placedWord.valid_intersections.append(coords)
        newWord.valid_intersections.append(coords)
        self.linked_letters_count+=1
    
    def filled_words(self):
        return len(self.current_words)

    def linked_letters(self):
        return self.linked_letters_count / 2

    def filled_ratio(self):
        total_letters = len(''.join([w.word for w in self.current_words]))
        corrected = total_letters - self.linked_letters()
        return corrected / (self.rows * self.cols)

    def linked_letters_ratio(self):
        return self.linked_letters() / (len(''.join([w.word for w in self.current_words])) - self.linked_letters())
    

    def scoreBoard(self):
        fw = self.filled_words()
        ll = self.linked_letters()
        fr = self.filled_ratio()
        lr = self.linked_letters_ratio()
        score = (fw + (0.5 * ll)) * fr * lr
        return score

    def schema(self):
        schema = {
            'across': {

            },
            'down': {

            }
        }

        for count, word in enumerate(self.current_words):
            word_details = {
                'clue': word.clue,
                'answer': word.word,
                'row': word.row,
                'col': word.col
            }
            if word.vertical:
                schema['down'][str(count)] = word_details
            else:
                schema['across'][str(count)] = word_details
        return schema

    def compute_crossword(self, time_permitted):
        print("computing crosswords now...")
        empty = duplicate(self)
        time_permitted = float(time_permitted)
        start = float(time.time())
        possible_cw = {}
        cw_scores = []
        while (float(time.time()) - start < time_permitted):
            copy = duplicate(empty)
            for word in copy.available_words:
                if word not in copy.current_words:
                    copy.try_place(word)
            
            board_score = copy.scoreBoard()
            cw_scores.append(board_score)
            possible_cw[board_score] = copy

        best = sorted(cw_scores)[-1]
        print("Best board")
        possible_cw[best].print_board()
        return possible_cw[best].schema()

class Word:
    def __init__(self, word=None, clue=None):
        self.word = word.lower()
        self.clue = clue
        self.len = len(self.word)
        self.row = None
        self.col = None
        self.vertical = None
        self.valid_intersections = []
    
    def get_surrounding_cells(self):
        neighbors = []
        cell = (self.row, self.col)
        for _ in self.word:
            if self.vertical:
                neighbors.extend([(cell[0], cell[1]-1), (cell[0], cell[1]+1)])
                cell = add_tuples(cell, (1,0))
            else:
                neighbors.extend([(cell[0]-1, cell[1]), (cell[0]+1, cell[1])]) 
                cell = add_tuples(cell, (0,1))

        bookends = self.get_bookend_cells()
        neighbors.extend(bookends)
        return neighbors 

    def get_bookend_cells(self):
        if self.vertical:
            return [(self.row-1, self.col), (self.row + len(self.word), self.col)]
        else:
            return [(self.row, self.col-1), (self.row, self.col + len(self.word))]

    def __repr__(self) -> str:
        return self.word
    


def schema_generator(crosswords):
        # { answer: clue }
        answers = sorted(crosswords.keys(), key = len, reverse = True)
        n = len(answers[0])
        cw = Crossword(n, n, gamedata=crosswords, available_words=answers)
        schema = cw.compute_crossword(3)
        return schema

def print_attributes(obj):
    for attr, value in obj.__dict__.items():
        print(f"{attr}: {value}")

def format_crossword(cw):
    formatted = {}
    for a, c in cw.items():
        formatted_a = a.lower()
        if ' ' in formatted_a:
            formatted_a = formatted_a.replace(' ', '')
            c += " (Two words.)"
    
        formatted[formatted_a] = c
    return formatted


if __name__ == "__main__":
    text = txtlib.SLOTH_FORMAL
    keywords = filter_keywords(keywords(text))
    crossword = format_crossword(clue_generator(keywords, text))
    schema = schema_generator(crossword)
    pprint.pprint(schema)