# -*- coding: utf-8 -*-

# CoreNet API
# Publisher: Key-Sun Choi, Machine Reading @ KAIST
# Copyright: CC BY-NC-ND
# API coding: Younggyun Hahm (hahmyg@kaist.ac.kr)

import pandas
import json
import re
from nltk.corpus import wordnet

def loadCoreNet():
    hanwoo = pandas.read_csv('./data/corenet/hanwoo.dat', skiprows=13, header=None, delimiter='\t', names=['idx','lemma','vocnum','semnum','definition','definition_added','usage'], index_col=['lemma'])

#    cndict = hanwoo.to_dict(orient='records')

    koWord = pandas.read_csv('./data/corenet/koWord.dat', skiprows=15, header=None, delimiter='\t', names=['idx','kortermnum','vocnum','semnum','nttnum','pos','chinese','japanese','korean'], index_col=['korean'])

#    kotermDict = koWord.to_dict(orient='records')

    cjkConcept = pandas.read_csv('./data/corenet/cjkConcept.dat', skiprows=14,header=None,delimiter='\t',names=['idx','kortermnum','parentkortermnum','nttnum','chinttname','japnttname','kornttname','gernttname'], index_col=['kortermnum'])

    wnLink = pandas.read_csv('./data/corenet/wnLink.dat',skiprows=4,header=None,delimiter='\t',names=['kortermnum','concept_en','wn_synset_rel'],index_col=['kortermnum'])
    kortermnum_list = []
    for index, row in wnLink.iterrows():
        kortermnum_list.append(index)

    goi2wn30 = pandas.read_csv('./data/corenet/goi2wn30.tab',skiprows=9,header=None,delimiter='\t',names  =['nttnum','wn3id','rel'],index_col=['nttnum'])

    return hanwoo, koWord, cjkConcept, wnLink, goi2wn30, kortermnum_list

hanwoo, koWord, cjkConcept, wnLink, goi2wn30, kortermnum_list = loadCoreNet()

# core API
def getHanwoo(arg):
    data = hanwoo.loc[[arg],['idx','vocnum','semnum','definition','usage']].to_dict(orient='records')
    return data

def getKorterm(lemma, vocnum, semnum):
    data = koWord.loc[[lemma],['vocnum','semnum','kortermnum']].to_dict(orient='records')
    kortermnum = ''
    l = kortermnum_list

    for i in data:
        if i['vocnum'] == vocnum and i['semnum'] == semnum:
            for j in l:
                if i['kortermnum'] == j:
                    kortermnum = i['kortermnum']
                    break
                else:
                    kortermnum = i['kortermnum']
    return kortermnum

def getPos(lemma, vocnum, semnum):
    data = koWord.loc[[lemma],['vocnum','semnum','pos']].to_dict(orient='records')
    pos = ''
    for i in data:
        if i['vocnum'] == vocnum and i['semnum'] == semnum:
            pos = i['pos']
    return pos


def getConceptName(kortermnum):
    data = cjkConcept.loc[[kortermnum],['kornttname']].to_dict(orient='records')
    concept = data[0]['kornttname']
    return concept

def getEnConceptName(kortermnum):
    n = 0
    for char in kortermnum:
        if char.isalpha():
            n = n+1
    if n == 0:
        kortermnum = kortermnum+' '
    else:
        kortermnum = kortermnum
    concept_en = wnLink.loc[[kortermnum],['concept_en']].to_dict(orient='records')
    return concept_en[0]['concept_en']

def getWordsInConcept(kortermnum):
    data = pandas.read_csv('./data/corenet/koWord.dat', skiprows=15, header=None, delimiter='\t',   names=['idx','kortermnum','vocnum','semnum','nttnum','pos','chinese','japanese','korean'], index_col=['kortermnum'])
    synonym = data.loc[[kortermnum],['vocnum','semnum','pos','korean']].to_dict(orient='records')
    return synonym

def getWn2id(kortermnum):
    n = 0
    for char in kortermnum:
        if char.isalpha():
            n = n+1
    if n == 0:
        kortermnum = kortermnum+' '
    else:
        kortermnum = kortermnum
    try:
        wn2id_raw = wnLink.loc[[kortermnum],['wn_synset_rel']].to_dict(orient='records')
        d = wn2id_raw[0]['wn_synset_rel']
        regex = re.compile('\^p(.*?)\^')
        wn2id = re.findall(regex, d)
    except:
        wn2id = 'None'
    return wn2id

def getWn3ids(kortermnum):
    nttnum = cjkConcept.loc[[kortermnum],['nttnum']].to_dict(orient='records')[0]['nttnum']
    wn3ids = goi2wn30.loc[[nttnum],['wn3id','rel']].to_dict(orient='records')#[0]['wn3id']
    return wn3ids

def getSynsets(kortermnum, only_synonym=False):
    synsets = []
    wn3ids = getWn3ids(kortermnum)
    for ids in wn3ids:
        offset = ids['wn3id']
        rel = ids['rel']
        if (rel == 'synonym' or not only_synonym):
            synset = wordnet.of2ss(offset)
            synsets.append(synset)
    return synsets


def getWnDefinition(wn2id):
    pos_regex = re.compile('(.*?):')
    wnid_regex = re.compile(':(.*)')
    def_regex_1 = re.compile('\| (.*?);')
    def_regex_2 = re.compile('\| (.*)')
#    wndf = 'None'
    wndfs = []
    for i in wn2id:
        pos = re.search(pos_regex, i).group(1)
        wnid = re.search(wnid_regex, i).group(1)
        if pos == 'v':
            path = './data/corenet/wnVerb.dat'
        elif pos == 'n':
            path = './data/corenet/wnNoun.dat'
        elif pos == 'aj':
            path = './data/corenet/wnAdj.dat'
        elif pos == 'av':
            path = './data/corenet/wnAdv.dat'
        else:
            print('ERROR in getWnDefinition')
            break

        with open(path, 'r') as f:
            for line in f:
                wnid_in_file = line.split()[0]
                if wnid == wnid_in_file:
                    if ';' in line:
                        wndf = re.search(def_regex_1, line).group(1)
                        wndfs.append(wndf)
                    else:
                        wndf = re.search(def_regex_2, line).group(1)
                        wndfs.append(wndf)
                    break
    return wndfs

def getCoreNet(arg):
    dt = getHanwoo(arg)
    for i in dt:
        semnum = i['semnum']
        vocnum = i['vocnum']
        lemma = arg

        kortermnum = getKorterm(lemma, vocnum, semnum)

        pos = getPos(lemma, vocnum, semnum)

        i['pos'] = pos
        i['kortermnum'] = kortermnum

        if kortermnum is not '':
            concept = getConceptName(kortermnum)
        else:
            concept = 'null'
        i['concept'] = concept
    return dt


# simple API

def getSemnum(arg):
    data = koWord.loc[[arg],['vocnum','semnum']].to_dict(orient='records')
#    data = hanwoo.loc[[arg],['vocnum','semnum']].reset_index().to_dict(orient='records')
    return data

def getDefinition(lemma, vocnum, semnum):
    data = hanwoo.loc[[lemma],['vocnum','semnum','definition']].to_dict(orient='records')
    definition = 'None'
    for i in data:
        if i['vocnum'] == vocnum and i['semnum'] == semnum:
            definition = i['definition']
#            break
    return definition

def getUsage(lemma, vocnum, semnum):
    data = hanwoo.loc[[lemma],['vocnum','semnum','usage']].to_dict(orient='records')
    usage = 'None'
    for i in data:
        if i['vocnum'] == vocnum and i['semnum'] == semnum:
            usage = i['usage']
#            break
    return usage



def getWnDef(lemma, vocnum, semnum):
    kortermnum = getKorterm(lemma, vocnum, semnum)
    wn2id = getWn2id(kortermnum)
    wndf = 'None'
    if wn2id is not 'None':
        wndf = getWnDefinition(wn2id)
    else:
        pass
    return wndf

def getWordnet(lemma, vocnum, semnum, only_synonym=False):
    wordnet_list = []
    wordnet_dict = {}
    kortermnum = getKorterm(lemma, vocnum, semnum)
    synsets = getSynsets(kortermnum, only_synonym=only_synonym)
    for synset in synsets:
        wordnet_dict = {}
        lemmas = []
        wordnet_dict['synset'] = synset
        wordnet_dict['definition'] = synset.definition()
        wn_lemma = synset.lemmas()
        for l in wn_lemma:
            lemma = l.name()
            lemmas.append(lemma)
        wordnet_dict['lemmas'] = lemmas
        wordnet_list.append(wordnet_dict)

    return wordnet_list

def getSynonymSynset(lemma, vocnum, semnum):
    return 0

def getSynonym(lemma, vocnum, semnum):
    kortermnum = getKorterm(lemma, vocnum, semnum)
    synonym = getWordsInConcept(kortermnum)
    return synonym


def getSimConcept(kortermnum):
    data = cjkConcept.loc[[kortermnum],['parentkortermnum']].to_dict(orient='records')
    pkn = data[0]['parentkortermnum']

    dt = pandas.read_csv('./data/corenet/cjkConcept.dat', skiprows=14,header=None,delimiter='\t',names=['idx','kortermnum','parentkortermnum','nttnum','chinttname','japnttname','kornttname','gernttname'], index_col=['parentkortermnum'])

    l = dt.loc[[pkn],['kortermnum']].to_dict(orient='records')
    simconcepts = []
    for i in l:
        c = i['kortermnum']
        simconcepts.append(c)
    return simconcepts

def get_all_words():
    dt = pandas.read_csv('./data/corenet/koWord.dat', skiprows=15, header=None, delimiter='\t', names=['idx','kortermnum','vocnum','semnum','nttnum','pos','chinese','japanese','lemma'], index_col=['idx'])
    l = []
    i = 1
    while i < 80718 :
        d = dt.loc[[i],['lemma','vocnum','semnum']].to_dict(orient='records')
        l.append(d)
        i = i+1
    return l





