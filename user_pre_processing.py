#!usr/bin/env python

import csv, json

class User:
    def __init__(self, userID, username, friend_count, follower_count,
        tweet_count, favourite_count):
        self.userID = userID
        self.username = username
        self.friend_count = friend_count
        self.follower_count = follower_count
        self.favourite_count = favourite_count

# Given the csv row of a user, format into the User class
# and convert to JSON, and append to list of user_json
def process_user(row):
    
    # Assume six attributes obtained from file  
    userID = row[0]
    username = row[1]
    friend_count = row[2]
    follower_count = row[3]
    tweet_count = row[4]
    favourite_count = row[5]

    user = User(userID, username, friend_count, follower_count, tweet_count,
        favourite_count)
    json_user = json.dumps(user.__dict__, sort_keys=True)
    return json_user

def write_file(json_content):
    write_filename = 'users.json'
    
    with open(write_filename, 'w+') as json_file:
        json_file.write(str(json_content))
     
def create_json_from_csv(filename):

    user_json_dict = {}
    user_json_list = []

    with open(filename, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            user_json_list.append(process_user(row))

    user_json_dict['Twitter_Users'] = user_json_list
    write_file(user_json_dict)

def main():
    filename = 'users.csv'
    create_json_from_csv(filename)

if __name__ == "__main__":
    main()
