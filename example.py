import corenet

d = corenet.getSemnum('먹다')
print(d)

d = corenet.getDefinition('먹다',0,4)
print(d)

d = corenet.getUsage('먹다',0,4)
print(d)

d = corenet.getKorterm('먹다',0,4)
print(d)

d = corenet.getConceptName('122221223')
print(d)

d = corenet.getWordnet('먹다',0,4,only_synonym=True)
print(d)


