# Anglicisms detection
====================================================

##I Module Transliteration.

Generated trans_hypothesis.txt file. It's a merge of files: Transcription and hypothesis from transliteration. 

Files:

1)  delete_on_slogi.py 

Input: diction.csv file with examples (Dyakov plus manully).

Algo: separate on slogi. Make statistics by bigrams of slogs and trigrams. Weighted. Return most possibles candidates for practical transliteration.
Takes Cirilization.txt. First column from this file. Generate for these words translit candidates and return file trans_hypothesis.txt where all trans hypotheses are.

Return: trans_hypothesis.txt file

====================================================

##II Hypotheses Intersection. LD

Make all hypothesis for anglicisms. Intersect the files form_roots.tsv and trans_hypothesis.txt 

Files:

1. form_roots.tsv -- 68647 words of normal form plus their roots.
1. trans_hypothesis.txt -- Look at I section
1. slovar_new.txt -- Zalizniak dictionary
1. suffixes.txt - список суффиксов
1. hypotheses_comparison.py -- file compare all possible variants by Levinshtein distance

(5) hypotheses_comparison.py

Input: Takes form_roots.tsv and trans_hypothesis.txt

Algo: 
- Takes all trans candidates+ english word and norm forms with roots. Check normal forms by Zalizniak ( about 6000 words stay!!!). 
- Two big sets (english + trans and russian forms + roots after Zalizniak filter) compare by Levinshtein distance. Check the length as well. Like so:
	if abs(len(root) - len(trans)) <= 2: # корень_рус - транскрипция_анг
        ed_dist = edit_distance(root, trans)
            if ed_dist < 2: ... 
    if abs(len(rus_word) - len(eng_word)) <= 4 etc.
- Write in table

Return:  Big table in format -- "eng_word, rus_word, type , root, trans, len(rus_word_or_root), len(eng_word_or_trans), ed_dist"

where type can be:
* "0" - for formal word
* "1" - for root
* "2" - composite

Proccess works infinity...
Better to separated form_roots.tsv on 10 parts and starts it up 10 times.

====================================================


##III Hypotheses check in Word2vec model.

* all_candidates.txt  - big table from section II.
* ./models/LJ_mincount30_window1_sg1_iter10.bin - word2vec model on LiveJournal
* take_best_candidates.py -- script that write what is in word2vec and ehat is not in it, but in our list. 


Input: Takes all_candidates and word2vec model.

Algo: Takes Russian candidates and check if the english word in top 200 similar latin word2vec candidates.

Return:  List of anglicisms / List of possible anglicisms that are not in word2vec.

====================================================
