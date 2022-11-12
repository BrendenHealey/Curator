import nltk
import random
import os
import pandas as pd
from nltk import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.stem.porter import *


def process(input):
    # Lowercase the user input
    tokens = word_tokenize(input.lower())
    # Declaring stemmer and lemmatizer
    wnl = WordNetLemmatizer()
    stemmer = PorterStemmer()
    # Performing both stemmer and lemmatizer on tokens
    tokens = [stemmer.stem(t) for t in tokens]
    tokens = [wnl.lemmatize(t) for t in tokens]
    tags = nltk.pos_tag(word_tokenize(input))
    pos_tagged = [t for t in tags if t[1] == 'NNP']

    # Testing
    print('Processed user input: ', tokens)
    print('NNP: ', pos_tagged)

    return tokens, pos_tagged


if __name__ == '__main__':
    THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
    kb = pd.read_csv(os.path.join(THIS_FOLDER, 'netflix_titles.csv'))
    #result = kb.loc[kb['description'].str.contains('family', case=False)]
    #print(result.sample())
    # Rule-based data where keyword is the trigger for response
    intents = [
        {'keyword': ['hello', 'hi', 'hey', 'howdy'], 'answer': ['Hi, could you tell me who you are?',
                                                                'Hello, can I get your name?',
                                                                'Greetings, human! Identify yourself!',
                                                                'Howdy Ho! What is your name?']},
        {'keyword': ['feeling'], 'answer': ['You are not the only one.', "I can't relate.",
                                            'I am not here to comfort you.']},
        {'keyword': ['name'], 'answer': ['How can I help you with ', 'What can I do for you  ']},
        {'keyword': ['like'], 'answer': ['Me too! ', 'I do not like ']},
        {'keyword': ['thanks', 'thank'], 'answer': ['It is my pleasure.', 'No problem!', 'You are welcome.']},
        {'keyword': ['year', 'release'], 'answer': ['Here are the movies and tv shows released in that year:']},
        {'keyword': ['about'], 'answer': ['Here are the matches with your description:']},
        {'keyword': ['genre'], 'answer': ['Here are the matches of your requested genre:']},
        {'keyword': ['act', 'actor'], 'answer': ['Here are the matches with your requested actor(s):']},
        {'keyword': ['direct', 'director'],
         'answer': ['Here are the matches directed by your requested director:']},
        {'keyword': ['titl', 'call'], 'answer': ['Here are the matches based on the search title:']},
        {'keyword': ['rate', 'rated'], 'answer': ['Here are the matches based on your requested rating:']},
        {'keyword': ['surprise', 'recommend'], 'answer': ['I recommend this movie/show:',
                                                          'I will bless you with this movie/show:']}
    ]

    while True:
        keyword = input("You: ")
        if keyword.lower() == 'exit':
            break
        keyword, pos_tags = process(keyword)
        received_answer = False
        for i in intents:
            for k in i['keyword']:
                if k in keyword:
                    print('Curator: ', random.choice(i['answer']))
                    if 'surprise' in keyword or 'recommend' in keyword:
                        if 'tv' in keyword:
                            result = kb.loc[kb['type'].str.contains('tv show', case=False)]
                            print(result.sample())
                        else:
                            result = kb.loc[kb['type'].str.contains('movie', case=False)]
                            print(result.sample())
                    elif 'titl' in keyword or 'call' in keyword:
                        title = " ".join(keyword[keyword.index(k)+1:])
                        result = kb.loc[kb['title'].str.contains(title, case=False)]
                        if len(result) > 5:
                            print(result.sample(5))
                        elif len(result) > 0:
                            print(result[0:])
                        else:
                            print("No matching title was found.")
                    elif 'about' in keyword:
                        result = kb.loc[kb['description'].str.contains(keyword[keyword.index(k)+1], case=False)]
                        print(result.sample(3))
                    received_answer = True
                    break
            if received_answer:
                break
        if not received_answer:
            print('Curator: I can not understand your statement, say something else.')
