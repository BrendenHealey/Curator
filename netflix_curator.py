import nltk
import random
import os
import pickle
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
    # POS Tagging
    tags = nltk.pos_tag(word_tokenize(input))
    # Extract Proper Nouns for Person
    pos_tagged = [t[0] for t in tags if t[1] == 'NNP']
    print(pos_tagged)

    return tokens, pos_tagged


if __name__ == '__main__':
    # Accessing knowledge base which is a spreadsheet of Netflix Movies and TV Shows
    THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
    kb = pd.read_csv(os.path.join(THIS_FOLDER, 'netflix_titles.csv'))
    pd.options.display.max_columns = None
    # Rule-based data where keyword is the trigger for response
    intents = [
        {'keyword': ['hello', 'hi', 'hey', 'howdy'], 'answer': ['Hi, could you tell me who you are?',
                                                                'Hello, can I get your name?',
                                                                'Greetings, human! Identify yourself!',
                                                                'Howdy Ho! What is your name?']},
        {'keyword': ['feel'], 'answer': ['You are not the only one', "I can't relate to",
                                         'I am not here to listen to you']},
        {'keyword': ['name', 'am'], 'answer': ['How can I help you?', 'What can I do for you']},
        {'keyword': ['like', 'love'], 'answer': ['I do', 'I do not']},
        {'keyword': ['hate'], 'answer': ['Understandable!', 'What a shame.']},
        {'keyword': ['thanks', 'thank'], 'answer': ['It is my pleasure.', 'No problem!', 'You are welcome.']},
        {'keyword': ['titl', 'call'], 'answer': ['Here are the matches based on the search title:']},
        {'keyword': ['genr'], 'answer': ['Here are the matches of your requested genre:']},
        {'keyword': ['about'], 'answer': ['Here are the matches with your description:']},
        {'keyword': ['act', 'actor'], 'answer': ['Here are the matches with your requested actor(s):']},
        {'keyword': ['direct', 'director'],
         'answer': ['Here are the matches directed by your requested director:']},
        {'keyword': ['rate'], 'answer': ['Here are the matches based on your requested rating:']},
        {'keyword': ['year'], 'answer': ['Here are the movies and tv shows released in that year:']},
        {'keyword': ['surpris', 'recommend'], 'answer': ['I recommend this movie/show:',
                                                         'I will bless you with this movie/show:']}
    ]

    # User Model
    user = {'name': None, 'like': None, 'hate': None}
    print('Curator is an informant and recommender of Netflix Movies and TV Shows Up to Mid-2021')
    while True:
        # Reading user input
        userInput = input("You: ")
        # Exit
        if userInput.lower() == 'exit' or userInput.lower() == 'quit':
            print('Curator: See you again!')
            print(user)
            if user['name'] is not None:
                file_name = user['name'] + '.txt'
                f = open(file_name, 'wb')
                pickle.dump(user, f)
                f.close()
            break
        # Keyword is used to trigger answer, entity is to identify the movie, actor, or director
        keyword, entity = process(userInput)
        received_answer = False
        for i in intents:
            for k in i['keyword']:
                if k in keyword:
                    # Personal Information Keywords
                    if 'name' in keyword or 'am' in keyword:
                        user['name'] = "".join(entity)
                        if os.path.exists(user['name']+'.txt'):
                            file_name = user['name'] + '.txt'
                            f = open(file_name, 'rb')
                            user = pickle.load(f)
                            f.close()
                            print('Curator: Nice to see you again,', entity[0],
                                  'who likes', user['like'],
                                  'and hates', user['hate']+'.',
                                  'How can I help you?')
                        else:
                            print('Curator: ', random.choice(i['answer']), " ".join(entity), "?")
                    elif 'like' in keyword:
                        print('Curator: ', random.choice(i['answer']), userInput[userInput.find('like'):])
                        user['like'] = userInput[userInput.find(entity[0]):]
                    elif 'love' in keyword:
                        print('Curator: ', random.choice(i['answer']), userInput[userInput.find('love'):])
                        user['like'] = userInput[userInput.find(entity[0]):]
                    elif 'hate' in keyword:
                        print('Curator: ', random.choice(i['answer']))
                        user['hate'] = userInput[userInput.find(entity[0]):]
                    elif 'feel' in keyword:
                        print('Curator: ', random.choice(i['answer']), userInput[userInput.find('feel'):])
                    # Random Suggestion
                    elif 'surpris' in keyword or 'recommend' in keyword:
                        print('Curator: ', random.choice(i['answer']))
                        if 'tv' in keyword:
                            result = kb.loc[kb['type'].str.contains('tv show', case=False)]
                            print(result.sample())
                        else:
                            result = kb.loc[kb['type'].str.contains('movie', case=False)]
                            print(result.sample())
                    # Search by Title
                    elif 'titl' in keyword or 'call' in keyword:
                        print('Curator: ', random.choice(i['answer']))
                        title = " ".join(keyword[keyword.index(k) + 1:])
                        result = kb.loc[kb['title'].str.contains(title, case=False)]
                        if len(result) > 3:
                            print(result.sample(3))
                        elif len(result) > 0:
                            print(result[0:])
                        else:
                            print("No matching title was found.")
                    # Search by Description
                    elif 'about' in keyword:
                        print('Curator: ', random.choice(i['answer']))
                        result = kb.loc[kb['description'].str.contains(keyword[keyword.index(k) + 1], case=False)]
                        if len(result) > 3:
                            print(result.sample(3))
                        elif len(result) > 0:
                            print(result[0:])
                        else:
                            print("No matching description was found.")
                    # Search Rating
                    elif 'rate' in keyword:
                        print('Curator: ', random.choice(i['answer']))
                        result = kb.loc[kb['rating'].str.contains(keyword[keyword.index(k) + 1], case=False)]
                        print(result.sample(3))
                    # Search Released Year
                    elif "year" in keyword:
                        print('Curator: ', random.choice(i['answer']))
                        result = kb.loc[kb['release_year'] == int(keyword[keyword.index(k) + 1])]
                        if len(result) > 3:
                            print(result.sample(3))
                        elif len(result) > 0:
                            print(result[0:])
                        else:
                            print("No movie was released in your requested year.")
                    # Search Genre
                    elif 'genr' in keyword:
                        print('Curator: ', random.choice(i['answer']))
                        result = kb.loc[kb['genre'].str.contains(keyword[keyword.index(k) - 1], case=False)]
                        print(result.sample(3))
                    # Search Director
                    elif 'direct' in keyword or 'director' in keyword:
                        print('Curator: ', random.choice(i['answer']))
                        result = kb.loc[kb['director'].str.contains(" ".join(entity), case=False, na=False)]
                        if len(result) > 3:
                            print(result.sample(3))
                        elif len(result) > 0:
                            print(result[0:])
                        else:
                            print("No matching director was found.")
                    # Search Actor
                    elif 'act' in keyword or 'actor' in keyword:
                        print('Curator: ', random.choice(i['answer']))
                        result = kb.loc[kb['cast'].str.contains(" ".join(entity), case=False, na=False)]
                        if len(result) > 3:
                            print(result.sample(3))
                        elif len(result) > 0:
                            print(result[0:])
                        else:
                            print("No matching actor was found.")
                    # General Talk
                    else:
                        print('Curator: ', random.choice(i['answer']))
                    received_answer = True
                    break
            if received_answer:
                break
        if not received_answer:
            print('Curator: I can not understand your statement, say something else.')
