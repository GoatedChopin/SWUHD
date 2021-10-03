import numpy as np
import pandas as pd
import re

tweets_file = np.load('public_tweets.npz',allow_pickle=True)

tweets_array = tweets_file['arr_0']

#Date Filtering
last_day = pd.to_datetime('2021/3/29')
first_day = pd.to_datetime('2020/3/6')
tweets_array = [tweet for tweet in tweets_array if tweet.created_at < last_day]

#Format Filtering
colon_format = re.compile('(Beaver\s*:|Garfield\s*:|Iron\s*:|Kane\s*:|Washington\s*:|County\s*:)')
end_tuple = re.compile('\(\d/\d\)\s*\n*')
end_digit = re.compile('\(\d\)\s*\n*')
integer = re.compile('\d*\,*\d{1,10}')

#Word Matching
counties = ['Beaver', 'Garfield', 'Iron', 'Kane', 'Washington']
counties_re = []
for county in counties:
    counties_re.append(re.compile(county))

column_types = ['new_cases_', 'total_cases_', 'deaths_', 'recoveries_', 'active_', 'previous_']
columns = []
for county in counties:
    for type in column_types:
        columns.append(type + county)

labels = ['new', 'total', 'death', 'recov', 'active', 'previously']
labels_re = []
for label in labels:
    labels_re.append(re.compile(label))

county_label_dict = {}
index = 0
for county in counties:
    column_dict = {}
    for label in labels:
        column_dict[label] = index
        index += 1
    county_label_dict[county] = column_dict

end_structure = {}
matches = 0
for tweet_object in tweets_array:
    tweet = tweet_object.text
    if colon_format.search(tweet):
        print(tweet, '\n')
        matches += 1
        if end_tuple.search(tweet):
            end_tuple_match = end_tuple.search(tweet)
            if end_tuple_match.end() == len(tweet):
                tweet = tweet[:end_tuple_match.start()]
        if end_digit.search(tweet):
            end_digit_match = end_digit.search(tweet)
            if end_digit_match.end() == len(tweet):
                tweet = tweet[:end_digit_match.start()]
        county_matches = []
        for county in counties_re:
            match = county.search(tweet)
            if match:
                county_matches.append([county.search(tweet).start(),county.search(tweet)])
        county_matches.sort(reverse=True)        
        
        label_matches = []
        for label in labels_re:
            lmatches = label.finditer(tweet)
            lmatches = [label for label in lmatches]
            label_matches.append(lmatches)
    
        integers = re.finditer(integer,tweet)
        integers = [i for i in integers]
        
        county_label_num_list = []
        for num in range(len(county_matches)):
            county_nums = []
            removal_ints = []
            
            for i in integers:
                columnid = county_label_dict[county_matches[num][1].group(0)]['total']
                for list in label_matches:
                    for label in list:
                        if i.end() == label.start() - 1:
                            columnid = county_label_dict[county_matches[num][1].group(0)][label.group(0)]
                        
                if i.start() > county_matches[num][1].start():
                    county_label_num_list.append([county_matches[num][1],
                                                  columnid,
                                                  i])
                    removal_ints.append(i)
                
            for int in removal_ints:
                integers.remove(int)
            
        for entry in county_label_num_list:
            if entry[1] < 5:
                ind = entry[1]
            else:
                new_num = entry[1]
                while new_num > 5:
                    new_num -= 6
                ind = new_num
                
            print(entry[0].group(0), str(entry[2].group(0)) + ' ' + labels[ind])
        print('\n')
        tweet_structure = []
        for i in range(30):
            tweet_structure.append(np.nan)
            
        for entry in county_label_num_list:
            tweet_structure[entry[1]] = entry[2].group(0)
        
        day_created = tweet_object.created_at.replace(hour=0, minute=0, second=0, microsecond=0)
        end_structure[day_created] = tweet_structure


df = pd.DataFrame.from_dict(end_structure, orient='index',columns=columns)
df.groupby(level=0).sum()

df.to_csv('dataframe_csv.csv')