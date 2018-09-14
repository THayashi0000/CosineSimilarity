# -*- coding: utf-8 -*-

import csv
import sys
import MeCab
import codecs
mecab = MeCab.Tagger("-Ochasen")
mecab.parse('')
terms = set([])
documents = []
usernames = []
stoplist = []
filename = 'input.csv'
#表の２列目には投稿ID、４列目には投稿文章が入っています
result_filename = filename[:-3] + 'result.csv'

with codecs.open('Japanese.txt', 'r', 'utf-8') as f:
    for line in f.readlines():
        stoplist.append(line.rstrip('\r\n'))

with codecs.open(filename, 'r', 'utf-8') as f:
    reader = csv.reader(f)
    for row in reader:
        node = mecab.parseToNode(row[3]).next
        documents.append(row[3])
        usernames.append(row[1])
        while node:
            if node.feature.split(",")[0] == "名詞":
                word = node.surface
                if word not in stoplist:
                    terms.add(word)
            node = node.next

def cosine_similarity(v1, v2):
    """
    ベクトルv1, v2のcos類似度の算出
    """
    return sum([a*b for a, b in zip(v1, v2)])/(sum(map(lambda x: x*x, v1))**0.5 * sum(map(lambda x: x*x, v2))**0.5)

def tf(terms, document):
    """
    :param terms:
    :param document:
    :return:
    """
    sys.stdout.write(".")
    sys.stdout.flush()
    tf_values = [document.count(term) for term in terms]
    return list(map(lambda x: float(x)/sum(tf_values), tf_values))


def idf(terms, documents):
    """
    :param terms:
    :param documents:
    :return:
    """
    import math
    print("start idf")
    return [math.log10(float(len(documents))/sum([bool(term in document) for document in documents])) for term in terms]


def tf_idf(terms, documents):
    """
    :param terms:
    :param documents:
    :return:
    """
    idf_result = idf(terms, documents)
    return [[_tf*_idf for _tf, _idf in zip(tf(terms, document), idf_result)] for document in documents]

terms = list(terms)
print("terms count: %d" % (len(terms)))
print("documents count: %d" % (len(documents)))

tf_idfs = tf_idf(terms, documents)
result_file = codecs.open(result_filename, 'w', 'utf-8-sig')
line = ""

for username in usernames:
	line += username + ","
result_file.write("UserName,"+line.strip(",")+"\n")

user_ycounter = 0
for yusername in usernames:
    line = ""
    user_xcounter = 0
    result_file.write(usernames[user_ycounter] + ",")
    for xusername in usernames:
        cosine_result = cosine_similarity(tf_idfs[user_ycounter], tf_idfs[user_xcounter])
        line += str(cosine_result) + ","
        user_xcounter += 1
    result_file.write(line.strip(",") + "\n")
    user_ycounter += 1
result_file.close()
