# -*- coding: utf-8 -*-
from __future__ import print_function
from datetime import datetime
import os, time, csv, json, fileinput

USER_ID = 'userID'
USERNAME = 'username'
FRIEND_COUNT = 'friend_count'
TWEET_COUNT = 'tweet_count'
FOLLOWER_COUNT = 'follower_count'
FAVOURITE_COUNT = 'favourite_count'

TYPE = 'type'
ORIGINAL = 'orig'
PROCESSED_TEXT = 'text'
EMBEDDED_URL = 'url'
TWEET_ID = 'id'
TIME_TWEETED = 'time'
RETWEET_COUNT = 'retNum'
FAVOURITE = 'fav'
MENTIONED_ENTITIES = 'ME'
HASHTAGS = 'HTs'

def main():
    # path to tweets
    path = '/Users/duongnguyen/Downloads/TwitterDataset/'
    # path = '/home/muha/Documents/TwitterDataset'
    
    filename = 'users.csv'
    json_filename = 'users.json'

    # create_json_from_csv(filename)
    # user_list = read_json(json_filename, user_decoder)

    PREV_TIME = time.time()
    # delete_empty_files(path)
    # filter_tweets(path)
    reformat_tweets(path)
    print('{0:.2f} seconds elapsed'.format(time.time() - PREV_TIME))


def filter_tweets(path):
    """
    Remove the tweets for which we have no user profile.
    """

    twitter_profile_ids = read_user_ids_csv()
    tweeters = read_tweeters(updated=False)
    files_deleted = 0
    
    files_to_delete = tweeters - twitter_profile_ids
    for ftd in files_to_delete:
        os.remove(path + 'tweets/' + ftd)
        files_deleted += 1

    print('Files deleted: {0}'.format(files_deleted))


def filter_user_profiles(path):
    """
    Remove the user profiles for which we have no tweets.
    """

    tweeters = read_tweeters(updated=False)
    user_profiles = []

    f = open('users.txt', 'r')
    for line in f:
        columns = line.split('\t')
        if len(columns) >= 6 and columns[0].isdigit() and columns[2].isdigit() and columns[3].isdigit() and \
           columns[4].isdigit() and columns[5].isdigit() and len(columns[1]) > 0:
            user_profiles.append([columns[0].strip(), columns[1].strip(), int(columns[2].strip()), 
                int(columns[3].strip()), int(columns[4].strip()), int(columns[5].strip())])

    f.close()
    print('Finished reading in user profiles...')

    user_profiles_of_tweeters = [profile for profile in user_profiles if profile[0] in tweeters]
    print('Finished filtering user profiles...')

    with open('users.csv', 'wb') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        csvwriter.writerows(user_profiles_of_tweeters)
    print('Finished writing to csv file...')


def reformat_tweets(path):
    """
    Open all Tweeter files and reformat tweets
    """

    tweeters = read_tweeters(updated=True)
    num_files = float(len(tweeters))
    counter = 0

    # create new files
    years = (2006, 2007, 2008, 2009, 2010, 2011)
    months = ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')
    for year in years:
        try:
            os.mkdir('{0}tweets_json/{1}'.format(path, year), 0775)
        except OSError:
            pass
        for month in months:
            with open('{0}tweets_json/{1}/{2}.json'.format(path, year, month), "wb") as myfile:
                myfile.write('[\n')

    print('Progress:')
    for tweeter in tweeters:
        with open(path + 'tweets/' + tweeter, 'r') as f:
            process_tweets(f.read(), path, tweeter)
            counter += 1
            print('{0:.2f}%'.format(round((counter/num_files)*100, 2)), end='\r')

    # finish off all files
    for year in years:
        for month in months:
            with open('{0}tweets_json/{1}/{2}.json'.format(path, year, month), 'rb+') as myfile:
                # remove last comma
                myfile.seek(-2, os.SEEK_END)
                myfile.truncate()
                myfile.write('\n]\n')


def process_tweets(content, path, tweeter):
    """
    Read tweets from file, process and convert to Json, write to new files
    grouped by the month they were posted instead of grouping by user
    """

    tweets = content.split('***\n***\n')
    tweets[0] = tweets[0].replace('***\n', '')
    tweets[-1] = tweets[-1].replace('***\n', '')

    try:
        for tweet in tweets:
            attributes = ('Type:', 'Origin:', 'Text:', 'URL:', 'ID:', 'Time:', 'RetCount:', 'Favorite:', 'MentionedEntities:', 'Hashtags:')
            values = []
            first = 0
            end = 0
            first = ''
            last = ''

            for i in xrange(len(attributes)-1):
                first = attributes[i]
                last = attributes[i+1]
                start = tweet.index(first, end) + len(first)
                end = tweet.index(last, start)
                values.append(tweet[start:end].strip())

            start = end + len(last)
            end = len(tweet)
            values.append(tweet[start:end].strip())

            value_iter = iter(values)

            t = value_iter.next()
            orig = value_iter.next()
            txt = value_iter.next()
            url = value_iter.next()
            ID = int(value_iter.next())
            time = value_iter.next()
            retNum = int(value_iter.next())
            fav = value_iter.next().lower() == 'true'
            ME = value_iter.next().split()
            HTs = value_iter.next().split()

            tweet = Tweet(t, orig, txt, url, ID, time, retNum, fav, ME, HTs)
            json_tweet = json.dumps(tweet.__dict__, sort_keys=True)

            # find file to append to
            toks = time.split()
            year = toks[-1]
            month = toks[1]
            if not year.isdigit() or not month.isalpha():
                raise Exception('Date processing error in file: {0}; year: {1}, month: {2}.'.format(tweeter, year, month))

            with open('{0}tweets_json/{1}/{2}.json'.format(path, year, month), "a") as myfile:
                myfile.write(json_tweet+',\n')
    except Exception as e:
        print('Encountered an error while processing file: {0}'.format(tweeter))
        print(e)


def clean_up_orig_tweet_files(path):
    """
    Remove invalid lines in tweet files
    """

    tweeters = read_tweeters(updated=True)
    num_files = 138022.0
    counter = 0
    line_starters = ('***', 'Type', 'Origin', 'Text', 'URL', 'ID', 'Time', 'RetCount', 'Favorite', 'MentionedE', 'Hashtags')

    print('Progress:')
    for tweeter in tweeters:
        #deleted_lines = []
        for line in fileinput.input(path + 'tweets/' + tweeter, inplace=True):
            if not line.startswith(line_starters):
                #deleted_lines.append(line)
                continue
            print(line, end='')
        #print('\n'.join(deleted_lines))
        
        counter += 1
        print('{0:.2f}%'.format(round((counter/num_files)*100, 2)), end='\r')

def delete_empty_files(path):

    tweeters = read_tweeters(True)
    files_deleted = 0

    for tweeter in tweeters:
        file_path = path + 'tweets/' + tweeter
        if (os.stat(file_path)[6] == 0):
            os.remove(file_path)
            files_deleted += 1

    print('Files deleted: {0}'.format(files_deleted))

def process_user(row):
    """
    Given the csv row of a user, format into the User class
    and convert to JSON, and append to list of user_json
    """
    
    # Assume six attributes obtained from file  
    userID = int(row[0])
    username = row[1]
    friend_count = int(row[2])
    follower_count = int(row[3])
    tweet_count = int(row[4])
    favourite_count = int(row[5])

    user = User(userID, username, friend_count, follower_count, tweet_count,
        favourite_count)
    return user

def process_user_from_json(user):
    userID = user[USER_ID]
    username = user[USERNAME]
    friend_count = user[FRIEND_COUNT]
    follower_count = user[FOLLOWER_COUNT]
    tweet_count = user[TWEET_COUNT]
    favourite_count = user[FAVOURITE_COUNT]

    user = User(userID, username, friend_count, follower_count, tweet_count,
        favourite_count)
    return user

def write_file(json_content):
    write_filename = 'users.json'
    
    with open(write_filename, 'w+') as json_file:
        json_file.write(json_content)
     
def create_json_from_csv(filename):
    user_json_list = [] 

    with open(filename, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            user_json_list.append(process_user(row))

    json_content = json.dumps([user.__dict__ for user in user_json_list],
            sort_keys=True, indent=4, separators=(',', ': '))
    write_file(json_content)

def user_decoder(obj):
    return User(obj[USER_ID], obj[USERNAME], obj[FRIEND_COUNT], obj[FOLLOWER_COUNT],
        obj[TWEET_COUNT], obj[FAVOURITE_COUNT])

def tweet_decoder(obj):
    return Tweet(obj[TYPE], obj[ORIGINAL], obj[PROCESSED_TEXT], obj[EMBEDDED_URL], obj[TWEET_ID],
        obj[TIME_TWEETED], obj[RETWEET_COUNT], obj[FAVOURITE], obj[MENTIONED_ENTITIES], obj[HASHTAGS])

def read_json(filename, decoder):
    with open(filename, 'r') as json_file:
        obj_list = json.load(json_file, object_hook=decoder)
        
    return obj_list

def read_user_ids_csv():
    twitter_profile_ids = set()
    
    with open('users.csv', 'rb') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in csvreader:
            twitter_profile_ids.add(row[0].strip())

    print('Twitter profile IDs read: {0}'.format(len(twitter_profile_ids)))
    return twitter_profile_ids


def read_tweeters(updated):
    tweeters = set()
    file_name = 'tweeters_updated.txt' if updated else 'tweeters.txt'
    
    with open(file_name, 'r') as tweeterfile:
        for line in tweeterfile:
            tweeters.add(line.strip())
    
    print('Number of Tweeters read: {0}'.format(len(tweeters)))
    return tweeters


class Tweet:
    def __init__(self, t, orig, text, url, ID, time, retNum, fav, ME, HTs):
        self.type = t
        self.orig = orig
        self.text = text
        self.url = url
        self.id = ID
        self.time = time
        self.retNum = retNum
        self.fav = fav
        self.ME = ME
        self.HTs = HTs


class User:
    def __init__(self, userID, username, friend_count, follower_count,
        tweet_count, favourite_count):
        self.userID = userID
        self.username = username
        self.friend_count = friend_count
        self.follower_count = follower_count
        self.tweet_count = tweet_count
        self.favourite_count = favourite_count


if __name__ == "__main__":
    main()
