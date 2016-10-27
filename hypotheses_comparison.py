import sys
import pprint
from collections import defaultdict
from difflib import SequenceMatcher

ZALIZNIAK = set()
with open('slovarnew.txt', 'r', encoding='utf-8') as zalizniak:
    for line in zalizniak.readlines():
        word_line = line.split(';')[0]
        [ZALIZNIAK.add(word.lower()) for word in word_line.split()]

with open('suffixes.txt', 'r', encoding='utf-8') as suffixes:
    suffixes = [suf.rstrip() for suf in suffixes.readlines()]

prefixes = ['не', 'по', 'за', 'пере', 'про', 'при', 'на', 'под', 'вы', 'раз', 'рас',
            'от', 'с', 'само', 'пред', 'об', 'полу', 'со', 'у', 'без', 'до',
            'бес', 'о', 'пре', 'ра', 'много', 'в', 'из']

stay_here = ['ин','ан','ап','оф', 'он']

def edit_distance(str1, str2):
     """
     Find edit distance between two words
     :param str1: string 1
     :param str2: string 2
     :return: number of edit distances
     """
     str1 = str1.replace('-','').replace(' ','')
     str2 = str2.replace('-', '').replace(' ', '')
     dic = {('к', 'с'):-0.5, ('а', 'е'):-0.5, ('э', 'а'):-0.5, ('е', 'э'):-0.5,
     ('а', 'э'):-0.5, ('с', 'к'):-0.5, ('е', 'а'):-0.5, ('э', 'е'):-0.5,
     ('й', 'и'):-1,('е', 'ё'):-1,('ё', 'е'):-1,('и','й'):-1, ('г', 'ж'):-1, ('ж','г'):-1}
     m, n = len(str1), len(str2)
     distance = [[0]*(n+1) for _ in range(m+1)]
     for i in range(m+1):
         distance[i][0] = i
     for j in range(n+1):
         distance[0][j] = j
     for i in range(1, m+1):
         for j in range(1, n+1):
             shtraf = dic.get((str1[i - 1], str2[j - 1]))
             if shtraf == None:
                 pannish = 1
             else:
                  pannish = shtraf
             insert = distance[i][j-1]+pannish
             deletion = distance[i-1][j]+pannish
             sub = distance[i-1][j-1]+(str1[i-1] != str2[j-1])
             distance[i][j] = min(insert, deletion, sub)
     return abs(distance[m][n])


def split_hashtag_to_words_all_possibilities(hashtag, word_dictionary):
    """
    Splitter. Makes hashtag splitting by slices.
    :param hashtag: compound word ex: олдскул
    :param word_dictionary: set of all transl candidadates
    return: ['олд',скул'']
    """
    all_possibilities = []

    split_posibility = [hashtag[:i] in word_dictionary for i in reversed(range(len(hashtag) + 1))]
    possible_split_positions = [i for i, x in enumerate(split_posibility) if x == True]

    for split_pos in possible_split_positions:
        split_words = []
        word_1, word_2 = hashtag[:len(hashtag) - split_pos], hashtag[len(hashtag) - split_pos:]

        if word_2 in word_dictionary:
            split_words.append(word_1)
            split_words.append(word_2)
            all_possibilities.append(split_words)

            another_round = split_hashtag_to_words_all_possibilities(word_2, word_dictionary)

            if len(another_round) > 0:
                all_possibilities = all_possibilities + [[a1] + a2 for a1, a2, in
                                                         zip([word_1] * len(another_round), another_round)]
        else:
            another_round = split_hashtag_to_words_all_possibilities(word_2, word_dictionary)

            if len(another_round) > 0:
                all_possibilities = all_possibilities + [[a1] + a2 for a1, a2, in
                                                         zip([word_1] * len(another_round), another_round)]

    return all_possibilities

def find_composites(rus_word, word_dictionary):
    """
    :param rus_word: Russian word
    :param word_dictionary: set of all transl candidadates
    :return: [compound1, compound2]
    """
    compound = split_hashtag_to_words_all_possibilities(rus_word, word_dictionary)
    if len(compound) > 0:
        new_compound = [comp for comp in compound if len(comp) == 2]
        if len(new_compound) > 0:
            print("URA!", new_compound)
            return new_compound[0]
    else:
        for suf in suffixes:
            if rus_word.endswith(suf):
                possible_compound = rus_word[:-len(suf)]
                compounds = split_hashtag_to_words_all_possibilities(possible_compound, word_dictionary)
                if len(compounds) > 0:
                    new_compound = [comp for comp in compounds if len(comp) == 2]
                    if len(new_compound) > 0:
                        print("URA!", new_compound)
                        return new_compound[0]
    return []


def find_best_candidates(eng_dic, root_dic, results, word_dictionary):
    """
    Write in big table all information
    :param eng_dic: dictionary {eng_word:(translit cand, cand, cand), (...),...}
    :param root_dic: dictionary {'russian_word':'root'}
    :param results: file in with I will write everything
    :param word_dictionary: set of all words candidates from translit
    """
    final_dic = defaultdict()
    for n, (rus_word, root) in enumerate(root_dic.items()): # все корни проверяем и русские слова

            compound = find_composites(rus_word, word_dictionary) # return if composite array of len 2
            if len(compound) == 2: # если композит, то
                for eng_word, trans_candidate_set in eng_dic.items():
                    for cand in trans_candidate_set:
                        ed = edit_distance(compound[0],cand)
                        ed2 = edit_distance(compound[1], cand)
                        if ed <= 1 and ed2 <= 1:
                            results.write("{},{},{},{},{},{},{},{}\n".format(eng_word, rus_word, "2", compound[0], cand, len(compound[0]), len(cand), ed))
                            results.write("{},{},{},{},{},{},{},{}\n".format(eng_word, rus_word, "2", compound[1], cand,
                                                                         len(compound[1]), len(cand), ed2))
            else:
                # если не композит, проверяем по всем гипотезам транслита для каждого английского слова
                for eng_word, trans_candidate_set in eng_dic.items():
                        for trans in trans_candidate_set:
                            if abs(len(root) - len(trans)) <= 2: # корень_рус - транскрипция_анг
                                    ed_dist = edit_distance(root, trans)
                                    if ed_dist < 2:
                                        # print(eng_word, rus_word, '1', root, trans, len(root), len(trans), ed_dist)
                                        results.write(
                                            "{},{},{},{},{},{},{},{}\n".format(eng_word, rus_word, '1', root, trans, len(root), len(trans), ed_dist))
                            if abs(len(rus_word) - len(trans)) <= 4:  # рус_слово - транск_англ
                                ed_dist3 = edit_distance(rus_word, trans)
                                if ed_dist3 < 4:
                                    # print(eng_word, rus_word, "0", '-', trans, len(rus_word), len(eng_word), ed_dist3)
                                    results.write(
                                    "{},{},{},{},{},{},{},{}\n".format(eng_word, rus_word, "0", '-', trans, len(rus_word), len(trans), ed_dist3))

                        # не загонять под цикл транс!
                        if abs(len(root) - len(eng_word)) <= 2:  # корень_рус - атнг слово
                            ed_dist2 = edit_distance(root, eng_word)
                            if ed_dist2 < 2:
                                # print(eng_word, rus_word, '1', root, '-', len(root), len(eng_word), ed_dist2)
                                results.write(
                                    "{},{},{},{},{},{},{},{}\n".format(eng_word, rus_word, '1', root, '-', len(root),
                                                                       len(eng_word), ed_dist2))
                        if abs(len(rus_word) - len(eng_word)) <= 4:  # рус_слово - англ слово
                            ed_dist4 = edit_distance(rus_word, eng_word)
                            if ed_dist4 < 4:
                                    # print(eng_word, rus_word, "0", '-', '-', len(rus_word), len(eng_word), ed_dist4)
                                    results.write(
                                    "{},{},{},{},{},{},{},{}\n".format(eng_word, rus_word, "0", '-', '-', len(rus_word), len(eng_word), ed_dist4))

            print("Current word: ", n, rus_word)
    return final_dic

def open_roots(path_to_root):
    """Read file with lemmas and roots. Write in dictionary.
    Return dic. format: {normal_form:root}"""
    root_dic = defaultdict()
    with open(path_to_root, 'r', encoding='utf-8') as roots:
        for line in roots.readlines():
            variants = line.split('\t')
            if variants[0] not in ZALIZNIAK:# reduce literal forms by Zalizniak
                root_dic[variants[0]] = variants[1].rstrip()
    return root_dic


def open_transc(filename):
    """Return: eng_dic - {real_eng_word: (cand, cand, cand...)}
    word_dictionary - all possible words"""
    word_dictionary = set()
    eng_dic = defaultdict()
    with open(filename, 'r', encoding='utf-8') as transcripts:
        for line in transcripts.readlines():
            tran_set = set()
            variants = line.split('@@@')
            for translit in variants[1].split('\t'):
                if len(translit) > 2:
                    if translit != '':
                        if translit not in stay_here:
                            tran_set.add(translit.rstrip())
                            word_dictionary.add(translit.rstrip())
            for var in variants[2].split('\t'):
                var = var.rstrip()
                if len(var) > 2:
                    if var != '':
                        if var not in stay_here:
                            tran_set.add(var)
                            word_dictionary.add(var)
            eng_dic[variants[0]] = tran_set
    return eng_dic, word_dictionary

if __name__ == "__main__":
    if len(sys.argv) == 3:
        path_to_root = sys.argv[1]
        number = sys.argv[2]

    path = './trans_hypothesis.txt'
    eng_dic, word_dictionary = open_transc(path)

    print("English transcripts dic done. Total word candidates number: ", len(word_dictionary))
    print("Total ENGLISH words number: ", len(eng_dic))

    root_dic = open_roots(path_to_root)
    print("Root candidates dic done", len(root_dic))

    with open(str(number)+'current_results.txt', 'a', encoding='utf-8') as results:
             ura_dic = find_best_candidates(eng_dic, root_dic, results, word_dictionary)

    # with open('results.csv', 'w', encoding='utf-8') as results:
    #         for key, value in ura_dic.items():
    #             results.write(key+"\t"+'\t'.join(value)+'\n')
