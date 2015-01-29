import sys
import math
import json
import redis
import bibtexparser
import nltk
import cfg

log = cfg.log

def main():
    # todo: handle the exception if redis is not available.
    log.info('Import citations into database...')
    r = redis.Redis(host=cfg.DB_HOST, port=cfg.DB_PORT)
    for filename in cfg.BIB_LIST:
        bibs = get_bibs(filename).entries_dict
        for key in bibs:
            for field in bibs[key]:
                r.hset(key, field, bibs[key][field].lower())
    r.save()
    log.info('Citations imported.')

    log.info('Counting words...')
    lexicon = {}
    abstracts = map(lambda key: r.hget(key, 'abstract').decode('utf-8'), r.keys())
    abstracts = list(filter(lambda e: e, abstracts))
    for abstract in abstracts:
        small_lexicon = get_lexicon(abstract)
        for word in small_lexicon:
            if word in lexicon:
                small_lexicon[word] += lexicon[word]
        lexicon.update(small_lexicon)
    log.info('Lexicon generated. (%d words)' % len(lexicon))

    log.info('Calculating IDF of each word...')
    lexicon_count_idf = {word: {
                            'count': lexicon[word], 
                            'idf': 0
                            }
                        for word in lexicon}
    for abstract in abstracts:
        small_lexicon = get_lexicon(abstract)
        for word in small_lexicon:
            lexicon_count_idf[word]['idf'] += 1

    for word in lexicon_count_idf:
        lexicon_count_idf[word]['idf'] = \
                math.log(len(abstracts) / lexicon_count_idf[word]['idf'])
    log.info('IDFs are all calculated.')

    log.info('Saving lexicon and IDFs...')
    with open(cfg.LEXICON_FILE, 'w', encoding='utf-8') as f:
        f.write(json.dumps(lexicon_count_idf, indent=4))
    log.info('Done.')


def get_bibs(filename):
    with open(filename, encoding='utf-8') as f:
        bib_str = f.read()
    return bibtexparser.loads(bib_str)


def get_lexicon(s):
    lexicon = {}
    words = nltk.word_tokenize(s.lower())
    wnl = nltk.stem.WordNetLemmatizer()
    for word in words:
        word = wnl.lemmatize(word)
        if word in lexicon:
            lexicon[word] += 1
        else:
            lexicon[word] = 1
    return lexicon


main()
