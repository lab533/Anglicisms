import gensim, re
from collections import defaultdict
import os

import pprint

class Word2vecModel:

    def __init__(self, top_number):
        self.top_number = top_number
        self.hyp_dictionary = defaultdict(list)
        self.new_model = \
            gensim.models.Word2Vec.load_word2vec_format('./models/LJ_mincount30_window1_sg1_iter10.bin', binary=True)
        self.temporal_ru_lat = defaultdict(list)
        self.temporal_lat_ru = defaultdict(list)
        
    def check_latin(self, word):
        """
        Check the word is latin or not
        :param word: one word string. candidate for anglizism
        :return: 1 if latin, 0 if not
        """
        word = word.split('_')[0]
        pattern = re.compile('^[a-zA-Z-]+$')
        if pattern.match(word)!= None:
            if not word.isupper():
                return 1
            else:
                return 0
        else:
            return 0

    def search_for_anglizism(self, word, eng):
        """
        Takes one word from word2vec model and check
        if there is an anglizism in top 20
        :param word: one word in format 'слово_S';
        :param eng: english word;
        :return latin_word: array of latin similar words;
        """
        similar_words = self.new_model.most_similar(word, topn=self.top_number)
        for candidate in similar_words:
            w2vcand = candidate[0].split("_")[0]
            if w2vcand == eng:
                return 1

    def load_model(self, hyp_set):
        """Load model and find anglizisms. Write current output in file"""
        print("Length of vocabulary", len(self.new_model.vocab))
        for item, (key, value) in enumerate(self.new_model.vocab.items()):
            try:
                word, gr = key.split('_')[0], key.split('_')[1]
                for eng, rus, ed, len_rus, len_eng in hyp_set:
                        if rus == word:
                            if self.search_for_anglizism(key, eng) == 1:
                                print("Anglicism: ", eng, rus, ed.rstrip())
                            else:
                                if abs(len(eng) - len(rus)) < 3:
                                    print('Lost: ', eng, rus, ed.rstrip())
            except:
                continue
        print('Filtered dictionaries done')


if __name__ == "__main__":


    w2v = Word2vecModel(200)

    with open('all_candidates.txt', 'r', encoding='utf-8') as big_data:
        hyp_set = set()
        for line in big_data.readlines():
            eng, rus, type, root, trans, len_rus, len_eng, ed = line.split(',')
            if float(ed) < 1:
                    if int(type) == 0:
                            hyp_set.add((eng, rus, ed, len_rus, len_eng))
                    elif int(type) == 1:
                            hyp_set.add((eng, root, ed, len_rus, len_eng))
                    else:
                            hyp_set.add((eng, root, ed, len_rus, len_eng))
        w2v.load_model(hyp_set)
