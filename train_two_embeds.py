#!/usr/bin/env python
# coding: utf-8


import glob
import gzip
import logging
import os
import re

import gensim
import pandas as pd

logging.basicConfig(format='%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                    datefmt='%Y-%m-%d:%H:%M:%S',
                    level=logging.INFO)


def deglutinate(emtsv_record):
    """
    Érdekelheti	" "	érdekel	[/V][_Mod/V][Prs.Def.3Sg]
    köszönhetően	" "	köszönhető	[/Adj][_Manner/Adv]
    """
    morphs = re.findall('\[[^/][^\]]*\]', emtsv_record.xpostag)
    # WONTFIX: prefixes (e.g. leg-)
    morphs = [morph for morph in morphs if morph not in ['[Nom]', '[Prs.NDef.3Sg]', '[Punct]']]
    # [Punct] is dropped, because the typical case  is "pl.", analized as [/Adv|Abbr][Punct]
    if morphs:
        return [emtsv_record.lemma] + morphs
    else:
        return [emtsv_record.form]


def get_sentences(file_pattern='2017_2018_2956', deglutinate_=False):
    """
    Yields a series for each sentence.
    """
    files = glob.glob(f'/mnt/permanent/home/ndavid/public_html/Webcorpus2_clean/{file_pattern}*.tsv.gz')
    for filen in sorted(files, key=os.path.getsize):
        logging.debug(filen)
        with gzip.open(filen, mode='rt') as textwrapper:
            word_records = []
            first_sent_in_file = True
            columns = None
            for line in textwrapper:
                line = line.strip()
                if not line:
                    if first_sent_in_file:
                        columns = word_records[0]
                        word_records = word_records[1:]
                        first_sent_in_file = False
                    sent_df = pd.DataFrame(word_records, columns=columns)
                    word_records = []
                    if deglutinate_:
                        if sent_df.empty:
                            logging.warning('empty sentence')
                            continue
                        yield sent_df.apply(deglutinate, axis=1).sum()
                    else:
                        yield list(sent_df.form)
                elif line.startswith('# newdoc id = '):
                    pass
                elif line.startswith('# newpar id = '):
                    pass
                elif line.startswith('# text = '):
                    pass
                else:
                    word_records.append(line.split('\t'))


for file_pattern in ['2017_2018_2956', '2017_2018_295', '2017_2018_29', 'wiki', '2017_2018_2', '2017_2018', '201', '']:
    for deglutinate_ in [False, True]:
        deglutinate_humanread = 'deglutAllSuffSepd' if deglutinate_ else 'vanila'
        logging.info((file_pattern, deglutinate_humanread))
        filen = f'/mnt/permanent/Language/Hungarian/Embed/webcorpus2.0/sgns-300-{file_pattern}-{deglutinate_humanread}'
        vocab_model_filen = f'{filen}-vocab.gensim'
        trained_model_filen = f'{filen}.gensim'
        if os.path.exists(trained_model_filen):
            logging.info(f'file exists: {trained_model_filen}')
        else:
            logging.debug(vocab_model_filen)
            if os.path.exists(vocab_model_filen):
                logging.info(f'loading {vocab_model_filen}')
                model = gensim.models.Word2Vec.load(vocab_model_filen)
            else:
                logging.info('building vocab..')
                model = gensim.models.Word2Vec(vector_size=300, sg=True)
                model.build_vocab(corpus_iterable=get_sentences(file_pattern=file_pattern, deglutinate_=deglutinate_))
                model.save(filen+'-vocab.gensim')
            logging.info('training model..')
            model.train(get_sentences(file_pattern=file_pattern, deglutinate_=deglutinate_),
                        total_examples=model.corpus_count, epochs=1)
            model.save(f'{filen}.gensim')
