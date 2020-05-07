from random import (
    choice,
    randint,
    shuffle
)

ALPHABET = [
    0,
    'a',
    'b',
    'c',
    'd',
    'e',
    'f',
    'g',
    'h',
    'i',
    'j',
    'k',
    'l',
    'm',
    'n',
    'o',
    'p',
    'q',
    'r',
    's',
    't',
    'u',
    'v',
    'w',
    'x',
    'y',
    'z'
]

CONSONANTS = [
    'b',
    'c',
    'd',
    'f',
    'g',
    'h',
    'j',
    'k',
    'l',
    'm',
    'n',
    'p',
    'q',
    'r',
    's',
    't',
    'v',
    'w',
    'x',
    'y',
    'z'
]

VOWELS = [
    'a',
    'e',
    'i',
    'o',
    'u'
]


def get_consonant():
    return choice(CONSONANTS)


def get_vowel():
    return choice(VOWELS)


def countdown_shuffle(plain_word):
    """
    Convert a Plain Text Word into a String of Jumbled Letters from the Original Plain Text Word.
    If the initial word is not 9 Letters long, add random Vowels & Consonants until the Length of the Jumble is 9.

    :param plain_word: (String) Plain Text Word to Jumble into Countdown Format
    :return: (String) Jumbled Word.
    """
    word_list = list(plain_word)
    shuffle(word_list)

    while len(word_list) < 9:
        index = randint(0, len(word_list))
        # Some considerations here:
        #   Don't always append to the start or end, this could skew our data.
        #   Don't always insert vowels at one side of the word and consonants at the other, or visa versa.
        if index % 2 == 0:
            word_list.insert(index, get_consonant())
        else:
            word_list.insert(index, get_vowel())

    return ''.join(word_list)


def encode_neural_network_example(word):
    """
    TODO: Description
    """
    return [ALPHABET.index(letter) for letter in word.lower()]


def encode_neural_network_label(word):
    """
    TODO: Description
    """
    encoded_list = [ALPHABET.index(letter) for letter in word.lower()]
    length = len(encoded_list)
    if length != 9:
        encoded_list += [0] * (9 - length)
    return encoded_list


def decode_word(encoded_word):
    return ''.join([str(ALPHABET[letter]) for letter in encoded_word])
