#!/usr/bin/env python
# coding: utf-8


import glob
import gzip
import logging
import os
import re

import gensim
import pandas as pd

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)


def deglutinate(emtsv_record):
    """
    Érdekelheti	" "	érdekel	[/V][_Mod/V][Prs.Def.3Sg]
    köszönhetően	" "	köszönhető	[/Adj][_Manner/Adv]
    """
    morphs = re.findall('\[[^/][^\]]*\]', emtsv_record.xpostag)
    # WONTFIX: prefixes (e.g. leg-)
    morphs = [morph for morph in morphs if morph not in ['[Nom]', '[Punct]']]
    if morphs:
        return [emtsv_record.lemma, "".join(morphs)]
    else:
        return [emtsv_record.form]


def get_sentences(file_pattern='2017_2018_2956', deglutinate_=False):
    """
    Yields a series for each sentence.
    """
    for filen in glob.glob(f'/mnt/permanent/home/ndavid/public_html/Webcorpus2_clean/{file_pattern}*.tsv.gz'):
        with gzip.open(filen, mode='rt') as textwrapper:
            word_records = []
            first_sent_in_file = True
            columns = None
            for line in textwrapper:
                line = line.strip()
                if not line:
                    if first_sent_in_file:
                        columns =  word_records[0]
                        word_records = word_records[1:]
                        first_sent_in_file = False
                    sent_df = pd.DataFrame(word_records, columns=columns)
                    word_records = []
                    if deglutinate_:
                        yield sent_df.apply(deglutinate, axis=1).sum()
                    else:
                        yield list(sent_df.form)
                elif line.startswith('#'):
                    if line.startswith('# text ='):
                        pass
                        # logging.debug = line[9:]
                else:
                    word_records.append(line.split('\t'))


for file_pattern in ['2017_2018_0']: # ['2017_2018_2956', '2017_2018_295', '2017_2018_29', '2017_2018_2', '2017_2018', '201', '']:
    for deglutinate_ in [False, True]:
        deglutinate_humanread = 'deglut' if deglutinate_ else 'vanila'
        logging.info((file_pattern, deglutinate_humanread))
        filen = f'/mnt/permanent/Language/Hungarian/Embed/webcorpus2.0/sgns-300-{file_pattern}-{deglutinate_humanread}'
        if os.path.exists(filen):
            logging.info('File exists')
            continue
        model_vanl = gensim.models.Word2Vec(vector_size=300, sg=True)
        model_vanl.build_vocab(corpus_iterable=get_sentences(file_pattern=file_pattern, deglutinate_=deglutinate_))
        model_vanl.save(filen+'-vocab')
        model_vanl.train(get_sentences(file_pattern=file_pattern, deglutinate_=deglutinate_), 
                         total_examples=model_vanl.corpus_count, epochs=1)
        model_vanl.save(filen)
