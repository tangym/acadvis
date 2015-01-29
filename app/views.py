# -*- encoding: utf-8 -*-
import redis
from flask import render_template, request
import nltk
from nltk.corpus import stopwords
import json
from app import app
import cfg

@app.route('/')
@app.route('/index')
def index():
    r = redis.Redis(host=cfg.DB_HOST, port=cfg.DB_PORT)
    s = request.args.get('s', '')
    if s:
        return ''
    else:
        bibs = map(lambda key: {field.decode('utf-8'): r.hget(key, field).decode('utf8') for field in r.hkeys(key)}, r.keys())
        # bibs = map(lambda key: r.hgetall(key), r.keys())  # why bytes?
        return render_template('index.html', bibs=list(bibs))

@app.route('/wordle')
def wordle():
    r = redis.Redis(host=cfg.DB_HOST, port=cfg.DB_PORT)
    with open(cfg.LEXICON_FILE) as f:
        s = f.read()
    lexicon = json.loads(s)
    print(len(lexicon))

    bibs = map(lambda key: {field.decode('utf-8'): r.hget(key, field).decode('utf8') for field in r.hkeys(key)}, r.keys())
    bibs = filter(lambda bib: 'abstract' in bib, bibs)
    abstracts = list(map(lambda bib: bib['abstract'], bibs))
    words = {}

    wnl = nltk.stem.WordNetLemmatizer()
    for abstract in abstracts[:50]:
        abstract = nltk.word_tokenize(abstract.lower())
        abstract = filter(lambda word: word not in stopwords.words('english'), abstract)

        punct = list(',./;\'[]\\`<>?:\"{}|~!@#$%^&*()_+-=')
        abstract = filter(lambda word: word not in punct, abstract)
        for word in abstract:
            word = wnl.lemmatize(word)
            if word in words:
                words[word] += 1
            else:
                words[word] = 1
    word_list = [[word, lexicon[word]['idf'] * words[word]] for word in words]
    word_list = sorted(word_list, key=lambda e: e[1], reverse=True)
    return render_template('wordle.html', word_list=word_list[:int(0.5*len(word_list))])



