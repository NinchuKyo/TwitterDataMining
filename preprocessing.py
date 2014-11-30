# -*- coding: utf-8 -*-
from __future__ import print_function
import os, time, csv, json, fileinput
from datetime import datetime

def main():
    # path to tweets
    path = '/home/muha/Documents/TwitterDataset/'

    PREV_TIME = time.time()
    reformat_tweets(path)
    print('{0:.2f} seconds elapsed'.format(time.time() - PREV_TIME))


def filter_tweets(path):
    """
    Remove the tweets for which we have no user profile.
    """

    twitter_profile_ids = set()
    tweeters = set()
    files_deleted = 0
    
    with open('users.csv', 'rb') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in csvreader:
            twitter_profile_ids.add(int(row[0]))
        print('Twitter profile IDs read: {0}'.format(len(twitter_profile_ids)))

        with open('tweeters.txt', 'r') as tweeterfile:
            for line in tweeterfile:
                tweeters.add(int(line))
            print('Number of Tweeters read: {0}'.format(len(tweeters)))

            files_to_delete = tweeters - twitter_profile_ids
            for ftd in files_to_delete:
                os.remove(path + 'tweets/' + str(ftd))
                files_deleted += 1

            print('Files deleted: {0}'.format(files_deleted))


def filter_user_profiles(path):
    """
    Remove the user profiles for which we have no tweets.
    """

    tweeters = set()
    user_profiles = []

    f = open('tweeters.txt', 'r')
    for line in f:
        tweeters.add(int(line))
    f.close()
    print('Finished reading in tweeters...')

    f = open('users.txt', 'r')
    for line in f:
        columns = line.split('\t')
        if len(columns) >= 6 and columns[0].isdigit() and columns[2].isdigit() and columns[3].isdigit() and \
           columns[4].isdigit() and columns[5].isdigit() and len(columns[1]) > 0:
            user_profiles.append([int(columns[0].strip()), columns[1].strip(), int(columns[2].strip()), 
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

    tweeters = set()
    num_files = 138022.0
    counter = 0

    with open('tweeters_updated.txt', 'r') as f:
        for line in f:
            tweeters.add(line.strip())

    # create new files
    years = [2007, 2008, 2009, 2010, 2011]
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
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
            lines = f.readlines()
            # if len(lines) % 12 != 0:
            #     raise Exception('File: {0}, lines: {1}.'.format(tweeter, len(lines)))
            process_tweets(lines, path, tweeter)
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


def process_tweets(lines, path, tweeter):
    """
    Read tweets from file, process and convert to Json, write to new files
    grouped by the month they were posted instead of grouping by user
    """
    try:
        for i in xrange(0, (len(lines) - (len(lines)%12)), 12):
            tweet_lines = lines[i:i+11]

            t = tweet_lines[1].split('Type:',1)[1].strip()
            orig = tweet_lines[2].split('Origin:',1)[1].strip()
            text = tweet_lines[3].split('Text:',1)[1].strip()
            url = tweet_lines[4].split('URL:',1)[1].strip()
            ID = int(tweet_lines[5].split('ID:',1)[1].strip())
            time = tweet_lines[6].split('Time:',1)[1].strip()
            retNum = int(tweet_lines[7].split('RetCount:',1)[1].strip())
            fav = tweet_lines[8].split('Favorite:',1)[1].strip().lower() == 'true'
            ME = tweet_lines[9].split('MentionedEntities:',1)[1].strip().split()
            HTs = tweet_lines[10].split('Hashtags:',1)[1].strip().split()

            tweet = Tweet(t, orig, text, url, ID, time, retNum, fav, ME, HTs)
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

    tweeters = set()
    num_files = 138022.0
    counter = 0
    line_starters = ('***', 'Type', 'Origin', 'Text', 'URL', 'ID', 'Time', 'RetCount', 'Favorite', 'MentionedE', 'Hashtags')

    f = open('tweeters_updated.txt', 'r')
    for line in f:
        tweeters.add(line.strip())
    f.close()
    print('Finished reading in tweeters...')

    print('Progress:')
    for tweeter in tweeters:
        deleted_lines = []
        for line in fileinput.input(path + 'tweets/' + tweeter, inplace=True):
            if not line.startswith(line_starters):
                deleted_lines.append(line)
                continue
            print(line, end='')
        #print('\n'.join(deleted_lines))
        
        counter += 1
        print('{0:.2f}%'.format(round((counter/num_files)*100, 2)), end='\r')


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


if __name__ == "__main__":
    main()
