from django import template
from Levenshtein import distance
from .censor_library import letters, bad_words


register = template.Library()
allow_value = 0.25


@register.filter()
def censor(value: str):
    if type(value) is not str:
        raise TypeError('Фильтр применён не к строке')

    words_orig = value.split()
    words = value.lower().split()
    new_words = []

    for key, val in letters.items():
        for lt in val:
            for word in words:
                for ch in word:
                    if ch == lt:
                        word = word.replace(ch, key)

    i = 0
    for word in words:

        new_word = words_orig[i]
        if word[0] in bad_words:
            word = word.translate({ord(i): None for i in '!.,:$#%^&'})
            for bw in bad_words[word[0]]:
                if distance(bw, word) <= len(word)*allow_value:
                    new_word = f'{words_orig[i][0]}' + '*' * (len(word) - 1)
                    break

        if len(new_word) == len(words_orig[i]):
            new_words.append(new_word)
        else:
            new_word += words_orig[i][len(new_word):]
            new_words.append(new_word)
        i += 1
    return ' '.join(new_words)