import pprint
import operator
from collections import defaultdict
from transliterate import translit
from itertools import product

vowels = 'aeyuio'
rus_vowel = 'уеыаоэяиюёй'

slogi_dic = defaultdict(lambda : defaultdict(int))

bigrams_dic = defaultdict(lambda : defaultdict(int))
# looks so: { 'c_a': {'к_а': 2, 'к_ей':1}, ... }

trigram_dic = defaultdict(lambda : defaultdict(int))
# looks so: { 'c_a_k': {'к_а_к': 2, 'к_ей_к':1}, ... }

re_slogi_dic = defaultdict(lambda : defaultdict(float))
re_bigrams_dic = defaultdict(lambda : defaultdict(float))
re_trigrams_dic = defaultdict(lambda : defaultdict(float))

def separate_slogs(word, vow='eng'):
    """Separate word on slogi with '|' """
    if vow == 'eng':
        vowels = 'aeyuio'
    else:
        vowels = 'уеыаоэяиюёй'
    was_already = 0
    global new_word
    new_word = ''
    for char1, char2 in zip(word, word[1:]):
        if char1 in vowels and char2 not in vowels:
            if was_already != 1:
                new_word += "|"+char1+"|"
        elif char1 in vowels and char2 in vowels:
            if was_already !=1:
                new_word += "|"+char1+char2+"|"
                was_already = 1
            else:
                new_word = new_word[:-1] + char2 + '|'
        else:
            new_word += char1
            was_already = 0
    if len(word) != len(''.join([w for w in new_word.split('|')])):
        if word[-1] in vowels:
            new_word += "|"+word[-1]
        else:
            new_word += word[-1]
    return new_word

def begin_end(word):
    """Added ^ and $ to word"""
    new_word = ''
    if word[0] == '|':
        new_word = "^|^"+word
    else:
        new_word = "^|^|"+word
    if word[-1] == "|":
        new_word = new_word + '$|$'
    else:
        new_word = new_word + "|$|$"
    return new_word

def make_bigram_trigram_dic(rus, eng):
    """
    Make bigrams and trigrams dictionary
    :param rus: array of slogs
    :param eng: array of clogs
    """
    for (r1, r2, r3), (e1, e2, e3) in zip(zip(rus, rus[1:], rus[2:]), zip(eng, eng[1:], eng[2:])):
        rus_big = r1 + "_" + r2
        eng_big = e1+ "_" +e2
        rus_trigram = r1 + "_" + r2 + "_" + r3
        eng_trigram = e1 + "_" + e2 + "_" + e3
        bigrams_dic[eng_big][rus_big] += 1
        trigram_dic[eng_trigram][rus_trigram] += 1


def make_freq_dic(rus_words, eng_words):
    for rus, eng in zip(rus_words, eng_words):
        rus = begin_end(rus)
        eng = begin_end(eng)
        rus_ar, eng_ar = rus.split("|"), eng.split("|")
        make_bigram_trigram_dic(rus_ar, eng_ar) # create bigram dic
        for r, e in zip(rus_ar, eng_ar):
            slogi_dic[e][r] += 1

def translite_formula(unigram, left, right,left_tri, right_tri):
    possible_candidates = defaultdict(int)
    for k, uni in unigram.items():
        left_val = left.get(k)
        right_val = right.get(k)
        left_val_tri = left_tri.get(k)
        right_val_tri = right_tri.get(k)
        if left_val == None: left_val = 0
        if right_val == None: right_val = 0
        if left_val_tri == None: left_val_tri = 0
        if right_val_tri == None: right_val_tri = 0
        score = uni * 0.1 + left_val* 0.3 + right_val*0.3 + left_val_tri*1.0 + right_val_tri* 1.0
        possible_candidates[k] = score
    try:
        cands = []
        for cand, val in possible_candidates.items():
            if val >= 0.03:
                cands.append(cand)
        return cands
        #     return max(possible_candidates.items(), key=operator.itemgetter(1))[0]
    except:
        return 0


def transliterate_word(word):
    """
    :param word: str - the word with ^, | and $
    :return: transliterated rus word
    unigram * w1 + left_bigram* w2 + right_bigram*w3 + left_trigram*w4 + right_bigram*w5
    w1 = 0.1, w2 = 0.2, w3 = 0.2, w4 = 0.3, w5 = 0.3
    """
    word_slogs = word.split('|')
    trans_words = []
    for w1, w2, w3, w4, w5 in zip(word_slogs, word_slogs[1:], word_slogs[2:], word_slogs[3:], word_slogs[4:]):
            unigram = re_slogi_dic[w3]
            bigram_left = re_bigrams_dic[w2+'_'+w3]
            bigram_right = re_bigrams_dic[w3+"_"+w4]
            trigram_left = re_trigrams_dic[w1+"_"+w2+"_"+w3]
            trigram_right = re_trigrams_dic[w3+"_"+w4+"_"+w5]
            global result_letter
            if len(unigram) == 0:
                result_letter = translit(w3, 'ru')
                trans_words.append((result_letter,))
            elif len(unigram) == 1:
                for key, val in unigram.items():
                    trans_words.append((key,))
            else:
                left = {left1.split('_')[1]: left2 for left1, left2 in bigram_left.items()}
                right = {r1.split("_")[0]: r2 for r1, r2 in bigram_right.items()}
                left_tri = {left1.split('_')[2]: left2 for left1, left2 in trigram_left.items()}
                right_tri = {r1.split("_")[0]: r2 for r1, r2 in trigram_right.items()}
                result_letter = translite_formula(unigram, left, right, left_tri, right_tri)
                trans_words.append(tuple(result_letter))
    candidates = list(product(*trans_words))
    new_candidates = [''.join(list(map(str, cand))) for cand in candidates]
    return new_candidates

def rewrite_dictionaries():
    """rewrite dictionaries in bool values"""
    for key, values in slogi_dic.items():
        all = sum(values.values())
        for k, val in values.items():
            re_slogi_dic[key][k] = val/all
    for key, values in bigrams_dic.items():
        all = sum(values.values())
        for k, val in values.items():
            re_bigrams_dic[key][k] = val/all
    for key, values in trigram_dic.items():
        all = sum(values.values())
        for k, val in values.items():
            re_trigrams_dic[key][k] = val/all


def open_new_set():
    """Open and process the new set of data to transliterate"""
    with open('cambridge_dic.csv', 'r', encoding='utf-8') as english:
        for line in english.readlines():
            word_sep = separate_slogs(line.rstrip(), vow='eng')
            translit = transliterate_word(begin_end(word_sep))
            print(line.rstrip(), translit)

if __name__ == "__main__":

    words, rus = [], []

    with open("diction.csv", 'r', encoding='utf-8') as dyakov:
        for line in dyakov.readlines():
            words.append(line.split(",")[0])
            rus.append(line.split(",")[1])

    eng_words = [separate_slogs(word, vow='eng') for word in words]
    rus_words = [separate_slogs(word.rstrip(), vow='rus') for word in rus]
    make_freq_dic(rus_words, eng_words)
    rewrite_dictionaries()

    # pprint.pprint(re_slogi_dic)
    # pprint.pprint(re_bigrams_dic)
    # pprint.pprint(re_trigrams_dic)
    # open_new_set()
    with open('trans_hypothesis.txt', 'w', encoding='utf-8') as hypothesis:
        with open('Cirilization.txt', 'r', encoding='utf-8') as trans_hyp:
            for line in trans_hyp.readlines():
                hyp_ar = line.split('@@@')
                word_sep = separate_slogs(hyp_ar[0], vow='eng')
                transliterations = transliterate_word(begin_end(word_sep))
                my_hyp = [hyp.replace('$','').replace('w','в').replace('q','кв') for hyp in transliterations
                          if len(hyp)-len(hyp_ar[0]) <= 1]
                # print(hyp_ar[0], '\t'.join(my_hyp))
                hypothesis.write(hyp_ar[0]+'@@@'+'\t'.join(my_hyp)+'@@@'+hyp_ar[2])