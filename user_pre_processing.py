#!usr/bin/env python

import csv, json

USER_ID = 'userID'
USERNAME = 'username'
FRIEND_COUNT = 'friend_count'
TWEET_COUNT = 'tweet_count'
FOLLOWER_COUNT = 'follower_count'
FAVOURITE_COUNT = 'favourite_count'

class User:
    def __init__(self, userID, username, friend_count, follower_count,
        tweet_count, favourite_count):
        self.userID = userID
        self.username = username
        self.friend_count = friend_count
        self.follower_count = follower_count
        self.tweet_count = tweet_count
        self.favourite_count = favourite_count

# Given the csv row of a user, format into the User class
# and convert to JSON, and append to list of user_json
def process_user(row):
    
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

# overloaded function for user-data read in JSON format
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

def read_json(filename):

    with open(filename, 'r') as json_file:  
        user_list = json.load(json_file, object_hook=user_decoder)
        
    return user_list

def main():

    filename = 'users.csv'
    json_filename = 'users.json'

    create_json_from_csv(filename)
    user_list = read_json(json_filename) 

if __name__ == "__main__":
    main()
