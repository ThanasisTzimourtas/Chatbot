import nltk
from nltk.stem.lancaster import LancasterStemmer
stemmer = LancasterStemmer()

import numpy
import tensorflow
import random
import json
import pickle
import tflearn
import webbrowser
import csv



FinalOrder = []
Pizzanames = []
Burgeranames = []
Order = []
Beernames = []
Refreshmentsnames = []
OrderRe = []


filemenu = open("menu1.csv", "r")
reader =  csv.reader(filemenu)

with open("chat_eng.json") as file:
    data = json.load(file)

try:
    with open("data.pickle", "rb") as f:
        words, labels, training, output = pickle.load(f)
except:
    words = []
    labels = []
    docs_user = []
    docs_tag = []

    for respones in data["responses"]:
        for pattern in respones["user"]:
            wrds = nltk.word_tokenize(pattern)
            words.extend(wrds)
            docs_user.append(wrds)
            docs_tag.append(respones["tag"])

        if respones["tag"] not in labels:
            labels.append(respones["tag"])

    words = [stemmer.stem(w.lower()) for w in words if w != "?"]
    words = sorted(list(set(words)))

    labels = sorted(labels)

    training = []
    output = []

    out_empty = [0 for _ in range(len(labels))]

    for x, doc in enumerate(docs_user):
        bag = []

        wrds = [stemmer.stem(w.lower()) for w in doc]

        for w in words:
            if w in wrds:
                bag.append(1)
            else:
                bag.append(0)

        output_row = out_empty[:]
        output_row[labels.index(docs_tag[x])] = 1

        training.append(bag)
        output.append(output_row)


    training = numpy.array(training)
    output = numpy.array(output)

    with open("data.pickle", "wb") as f:
        pickle.dump((words, labels, training, output), f)

tensorflow.reset_default_graph()

net = tflearn.input_data(shape=[None, len(training[0])])
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, len(output[0]), activation="softmax")
net = tflearn.regression(net)

model = tflearn.DNN(net)

try:
    model.load("model.tflearn")
except:
    model = tflearn.DNN(net)
    model.fit(training, output, n_epoch=1000, batch_size=8, show_metric=True)
    model.save("model.tflearn")
 
    
 
    
def bag_of_words(s, words):
    bag = [0 for _ in range(len(words))]

    s_words = nltk.word_tokenize(s)
    s_words = [stemmer.stem(word.lower()) for word in s_words]

    for se in s_words:
        for i, w in enumerate(words):
            if w == se:
                bag[i] = 1
            
    return numpy.array(bag)


def categorynames():
    for row in reader:
        if (row[1] == 'pizza'):
            Pizzanames.append([row[2],row[3]])
        
        if (row[1] == 'burger'):
            Burgeranames.append([row[2],row[3]])
            
        if (row[1] == 'beer'):
            Beernames.append([row[2],row[3]])
            
        if (row[1] == 'refreshments'):
            Refreshmentsnames.append([row[2],row[3]])



def chat():
    print("Hi Costumer, welcome to the Burger House!\nType quit to stop!")
    while True:
        categorynames()
        inp = input("You: ")
        if inp.lower() == 'pizza':
            print('\nOur Menu for Pizza is: \n')
            for p, pp in Pizzanames:
                print('{} only {} €'.format(p,pp))
            print('\nIf you changed your mind you can always see our delicious Burger offers by typing burger!!!')
            
        if inp.lower() == 'burgers':
            print('\nOur Menu for Burger is: \n')
            for b, bp in Burgeranames:
                print('{} only {} €'.format(b,bp))
            print('\nIf you changed your mind you can always see our delicious Pizza offers by typing pizza !!!')
            
        if inp.lower() == 'beers':
            print('\nOur Menu for Beers is: \n')
            for br, pbr in Beernames:
                print('{} only {} €'.format(br,pbr))
            print('\nIf you changed your mind you can always check our refreshments, by typing refreshments ')
            
        if inp.lower() == 'refreshments':     
            print('\nOur Menu for Refreshments is: \n')
            for ref, pref in Refreshmentsnames:
                print('{} only {} €'.format(ref,pref))
            print('\nIf you changed your mind you can always check our beers by typing Beers ')
            
        if inp.lower() == 'maps':
            webbrowser.open('https://www.google.com/maps/search/burger+house/@38.0383127,23.8203109,13z/data=!3m1!4b1')
        
        if inp.lower() == 'order':
            print('When you finish you order, type: Done')
            food_order = input('\nPlease enter your order here: ')
            while (food_order != 'Done'):
                Order.append(food_order)
                food_order =input('\nAnd what else?: ')
            print('\nYour order was: \n')
            for items in Order:
                print(items)
            address = input('Please give me an address: ')
            print('\nYour order will be in the address {} in 35 min'.format(address))
    
        if inp.lower() == "quit":
            break

        results = model.predict([bag_of_words(inp, words)])
        result_max = numpy.argmax(results, axis = None, out = None)
        tag = labels[result_max]

        for tg in data["responses"]:
            if tg['tag'] == tag:
                responses = tg['chatbot']

        print(random.choice(responses))

chat()
