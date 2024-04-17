
SLOTH_CASUAL = '''
    the dodo may be forever associated with extinction but it's certainly not the
    first to disappear forever 13,000 years ago retreating eyes and the spread of
    angry people saw the beginning of a major extinction event that engulfed
    thousands of species and continues today the first animals to be targeted with a megafauna
    huge almost fantastical creatures and when in recent history the fossils of
    megafauna began to emerge people were as intrigued as they were confused do you
    know what to do a dinosaur this is a dinosaur Jane I
    miss it he's a mediator two ranks koala the man who can tell us
    what it is is paleontology curator Andy current this animals called make the
    cerium marvelous name but all it means is big animal but it's better known as
    the giant ground sloth it's just amazing pictures great the giant ground sloth was an animal that
    once roamed the grasslands of South America 10,000 years ago
    but ever since his discovery in Brazil in 1789 misunderstandings about the
    giant sloth have continued a skeleton was brought back to Madrid and put on
    display in a museum there it is mounted remarkably like a coffee table it
    doesn't look like a real animal and thatto me is the endearing quality of this
    particular specimen the way it's constructed obviously is not moving but
    it looks as though it can move and I think that's exciting
    despite its looming presence the giant sloth was a gentle herbivore not really
    built for speed it weighed in at over two tons
    Megatherium reminds me of an old man in carpet slippers the feat is rather
    distorted it turned over on their side other men with arthritis
    megatherium was one of the first animals to disappear in the period of extinction that continues today I fell in love with
    this thing our first order as far as I'm concerned this is the best exhibit in the museum brilliant
'''

SLOTH_FORMAL = '''
    Ground sloths are a diverse group of extinct sloths in the mammalian superorder Xenarthra. Ground sloths varied widely in size, with the largest genera Megatherium and Eremotherium being around the size of elephants. Ground sloths are a paraphyletic group, as living tree sloths are thought to have evolved from ground sloth ancestors.
The early evolution of ground sloths took place during the late Paleogene and Neogene of South America, while the continent was isolated. At their earliest appearance in the fossil record, the ground sloths were already distinct at the family level. Sloths dispersed into the Greater Antilles during the Oligocene, and the presence of intervening islands between the American continents in the Miocene allowed a dispersal of some species into North America, They were hardy as evidenced by their high species diversity and their presence in a wide variety of environments, extending from the far south of Patagonia (Cueva del Milodón Natural Monument) to Alaska.[1][2][3] Sloths, and xenarthrans as a whole, represent one of the more successful South American groups during the Great American Interchange after the connection of North and South America during the late Pliocene with a number of ground sloth genera migrating northwards. One genus, Thalassocnus, even adapted for marine life along the Pacific coast of South America during the late Miocene and Pliocene epochs.
Ground sloths, which were represented by over 30 living species during the Late Pleistocene, abruptly became extinct on the American mainland as part of the Late Pleistocene extinctions at the end of the Pleistocene, around 12,000 years ago simultaneously along with most other large mammals in the Americas. Their extinction has been posited to be the result of hunting by recently arrived humans and/or climate change.[4][5] A number of kill sites are known where humans butchered ground sloths dating just prior to their extinction.
The Caribbean ground sloths, the most recent survivors, lived in the Antilles, possibly until 1550 BCE. However, radiocarbon dating suggests an age of between 2819 and 2660 BCE for the last occurrence of Megalocnus in Cuba.[6] They survived 5,000–6,000 years longer in the Caribbean than on the American mainland, which correlates with the later colonization of this area by humans.[7]

'''

KEYWORD_EXTRACT = '''
    You are a crosswords game expert.
    Extract keywords from the following text to be used as clues in a crosswords game.

    TEXT: {paragraph}

    Follow these steps:
    1. Select the best keywords from the text that would make good answers in crosswords.
    2. Put your selected keywords into a JSON file under the key: 'keywords'.

    Use JSON.
    
'''

CLUE_GENERATOR = '''
    You are a crosswords expert.
    Generate short and clever clues for
    crosswords, based on a list of keywords
    and a keyword-related context,
    following the instructions provided below.
    KEYWORDS: {keywords}
    CONTEXT: {text}
    Follow these steps for each keyword in your list of keywords:
    1. Find parts of the given context related
    to the keyword.
    2. Select one key piece of information
    related to the keyword and that
    are present in the context.
    3. Create short clues from this key
    fact, making sure not to include the
    keyword in the clues.
    4. Put these clues into a JSON file under
    the key: 'clues'.
'''