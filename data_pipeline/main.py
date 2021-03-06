####De fouten waar ik nu op vast loop:
#De resultaten komen een voor een binnen. Mijn code stopt dus als de 
#JSON file binnen komt, ook al is dit een error code 403. Hiernaast:

#Op de website zie ik dat ik verschillende error codes krijg: 
#zowel een 429 als een 403. Ik zie echter bij mijn functie alleen de eerste keer
#gewoon netjes een code 200. Ik weet ook niet hoe ik deze code goed kan ophalen
#zodat ik kan checken of het ook echt 200 is.

from API_calls import obtainUserJSON
from API_calls import singleUserID
from API_calls import singleUserFollowers

from API_calls import updateCollection
from API_calls import showCollection
from API_calls import replaceCollection

from API_calls import workflowCall_postTimerange
from API_calls import workflowCall
from API_calls import executeWorkflow

from API_calls import workflowExecutionsJSON
from API_calls import workflowExecutionIDS
from API_calls import executionDetails
from API_calls import storeJSON

from API_calls import checkSessionID

from samplesize import calculate_samplesize
from API_calls import obtainSample
from API_calls import createFollowerdf

import requests
from datetime import datetime
import pandas as pd
import json
import random
import time
import math
import urllib.request as ur
from datetime import datetime
import argparse

#Loading in some data I will need
URL_BASE = 'https://stevesie.com/cloud/api/v1'
API_TOKEN = "XXXXXXXXXXXXXXXXXXXXX" # SECRRET <-- IF YOU WANT ONE PLEASE VISIT STEVESIEDATA.ORG

auth_headers = {
  'Token': API_TOKEN,
}

#Session IDs of three of my accounts.
sessionIDs = {
"Instauser" : "2XXXXXXXXXXXXXXXXXXXXX" #  SECRRET <-- IF YOU WANT TO USE ENTER THE SESSION ID OF YOUR OWN INSTAGRAM ACCOUNT.
 }


#My workflows with their corresponding collections
workflows = {
   "postsTimerange_new" : {"workflowID" : "bfa05c12-f566-4368-8675-735a0dc5f6b9",
                       "collections" : {"userIDs" : "1aa18fd4-d071-406d-96dc-e27bafe4bbca"}
                        },
    "followers_new" : {"workflowID" : "ed8a59aa-b40a-497e-b20c-175109e15123",
                  "collections" : {"sessionIDs" : "ef6e6d52-b9e7-41ee-b6f5-b761d39984df",
                                  "userIDs" : "fa0ae2c5-88cd-4527-ad71-ce39cc243c65"}
                  }

}


def randomSessionIDS(sessionIDs, n):
    """This function randomly picks n sessions IDs based on the collection of sessionIDs you have."""
    return random.sample([sessionIDs[value] for value in sessionIDs], n)

def checkValidityID(sessionID, API_TOKEN, user_id='9623334065'):
    """This function very simply checks whether a session ID is working."""
    response_json = requests.post(
    'https://stevesie.com/cloud/api/v1/endpoints/cb390e0f-57ad-4c26-bdfb-8dcc233677d5/executions',
    headers={ 'Token': API_TOKEN },
    json={
        'inputs': {
            'user_id': user_id,
            'session_id': sessionID,
        },
        'proxy': {
          'type': 'shared',
          'location': 'nyc',
        },
        'format': 'json'
    },).json()
    try:
        response_json['object']['response']['response_json']['user']['public_email']
        return True
    except:
        return False

def main(profileName, run, followerLoc, workflows, sessionIDs, API_TOKEN, URL_BASE = 'https://stevesie.com/cloud/api/v1'):
    session_number = 2
    print(profileName)
    """Give this function an Instagram username as input. It will create a 
    CSV file which executes the four steps described in the README.txt file."""
    #Randomly select three sessionIDs we are going to use for this execution.
    chosen_sessionIDs = randomSessionIDS(sessionIDs, 1)
    while checkValidityID(chosen_sessionIDs[0], API_TOKEN) == False:
        print('Error - The chosen sessionID was not valid: {}'.format(chosen_sessionIDs[0]))
        chosen_sessionIDs = randomSessionIDS(sessionIDs, 1)
    ########### STEP 1 - OBTAIN INFORMATION REGARDING THE USER
    userJSON = obtainUserJSON(profileName, chosen_sessionIDs[0], API_TOKEN)
    userID = singleUserID(userJSON)
    userFollowers = singleUserFollowers(userJSON)   

    ########### STEP 2 - OBTAINING THE USERS ITS FOLLOWERS WITH THE FOLLOWERS IDS WORKFLOW
    #First empty the sessionID collection and fill with three new random values.
    #We check whether this is the first profile we build. Otherwise we just obtain the user
    #names from the followers.json file that is in the data folder.
    if run != 'first':
        print("INFO - As opposed we will create another follower profile for {}".format(profileName))

        if followerLoc == 'second':
            with open('../rawdata/{}_second_followers.json'.format(profileName)) as json_file:
                userFollowersJSON = json.load(json_file)
        elif followerLoc:
            with open('../rawdata/{}'.format(followerLoc)) as json_file:
                userFollowersJSON = json.load(json_file)
        else:
            with open('../rawdata/{}_followers.json'.format(profileName)) as json_file:
                userFollowersJSON = json.load(json_file)

        stored_nameDict = createFollowerdf(userFollowersJSON)
        #I only want to extract the usernames which have private settings on False
        nonPrivate_nameDict = stored_nameDict.loc[stored_nameDict['private'] == False]
        # All IDS we extracted, now we just have to remove the names we already scraped.
        all_IDS = [value for value in nonPrivate_nameDict['username']]
        # Now we take a look at the follower profile we already created. We do not want
        # to extract posts from these usernames again!
        if run == 'fourth':
            post_df_1 = pd.read_csv('../rawdata/{}_followerProfile.csv'.format(profileName))
            post_df_2 = pd.read_csv('../rawdata/{}_second_followerProfile.csv'.format(profileName))
            post_df_3 = pd.read_csv('../rawdata/{}_third_followerProfile.csv'.format(profileName))
            extracted_IDS_1 = [value for value in [value for value in set(post_df_1['data.user.edge_owner_to_timeline_media.edges.node.owner.username'])]]
            extracted_IDS_2 = [value for value in [value for value in set(post_df_2['data.user.edge_owner_to_timeline_media.edges.node.owner.username'])]]
            extracted_IDS_3 = [value for value in [value for value in set(post_df_3['data.user.edge_owner_to_timeline_media.edges.node.owner.username'])]]
            extracted_IDS = extracted_IDS_1 + extracted_IDS_2 + extracted_IDS_3
        elif run == 'third':
            post_df_1 = pd.read_csv('../rawdata/{}_followerProfile.csv'.format(profileName))
            post_df_2 = pd.read_csv('../rawdata/{}_second_followerProfile.csv'.format(profileName))
            extracted_IDS_1 = [value for value in [value for value in set(post_df_1['data.user.edge_owner_to_timeline_media.edges.node.owner.username'])]]
            extracted_IDS_2 = [value for value in [value for value in set(post_df_2['data.user.edge_owner_to_timeline_media.edges.node.owner.username'])]]
            extracted_IDS = extracted_IDS_1 + extracted_IDS_2
        elif run == 'second':
            post_df = pd.read_csv('../rawdata/{}_followerProfile.csv'.format(profileName))
            extracted_IDS = [value for value in post_df['data.user.edge_owner_to_timeline_media.edges.node.owner.username']]
        else:
            print('ERROR - Shutdown code! We currently only created code for a first, second or third run!')
        #These are all the names we have not scraped yet!
        valid_usernames = [name for name in all_IDS if name not in extracted_IDS]
        #Check whether we should extract more usernames.
        print("INFO - Currently we stored {} userIDs which can be scraped.".format(len(nonPrivate_nameDict)))
        print("INFO - Need to scrape a total of {} userIDs".format(calculate_samplesize(userFollowers)))
        print("INFO - Already scraped {} userIDs. Therefore, {} left to scrape.".format(len(set(extracted_IDS)), len(valid_usernames)))
        
        #In this block we create a second json file with followernames we can scrape. We do this because
        #intially there were not enough public profiles in the first dataset that could be scraped.
        if len(valid_usernames) < (1 * calculate_samplesize(userFollowers)):
            print("INFO - We did not have 2.5 times the number of profiles we still want to scrape. Therefore, we will extend the number of profiles.")
            replaceCollection(workflows['followers_new'.format(session_number)]['collections']['sessionIDs'], chosen_sessionIDs, API_TOKEN)    
            replaceCollection(workflows['followers_new'.format(session_number)]['collections']['userIDs'], [userID], API_TOKEN)
            if userFollowers < 1000 : proxyType = 'shared'
            else : proxyType = 'dedicated'
            #We now extract a very large amount of profile to be sure we have enough due to this second collection we create.
            userFollowersJSON = executeWorkflow(workflows['followers_new']['workflowID'], API_TOKEN, proxyType, 'json', profileName, 2000)
            storeJSON(userFollowersJSON, profileName+"_second_followers")
            #Now we can use the new names to extract a new set of valid_usernames.
            stored_nameDict = createFollowerdf(userFollowersJSON)
            nonPrivate_nameDict = stored_nameDict.loc[stored_nameDict['private'] == False]
            all_IDS = [value for value in nonPrivate_nameDict['username']]
            valid_usernames = [ID for ID in all_IDS if ID not in extracted_IDS]
            print("INFO - Finished creating a second json file with follower names to scrape.")
        
        nameDict = nonPrivate_nameDict[nonPrivate_nameDict['username'].isin(valid_usernames)]

    #If this is the first time we run the script....
    else:
        replaceCollection(workflows['followers_new'.format(session_number)]['collections']['sessionIDs'], chosen_sessionIDs, API_TOKEN)
        #Now we also do this process for the collection ID containing the userIDs
        replaceCollection(workflows['followers_new'.format(session_number)]['collections']['userIDs'], [userID], API_TOKEN)
        #Collections replaced; now we can run the workflow. If followers below 750 than its cheaper to run shared proxy.
        if userFollowers < 1000 : proxyType = 'shared'
        else : proxyType = 'dedicated'
        userFollowersJSON = executeWorkflow(workflows['followers_new']['workflowID'], API_TOKEN, proxyType, 'json', profileName, 2000)
        #Executing a function to store this result in the data folder so nothing is lost
        storeJSON(userFollowersJSON, profileName+"_followers")
        nameDict = createFollowerdf(userFollowersJSON)

    sampledf = obtainSample(nameDict, userFollowers)
    
    ########### STEP 3 - OBTAINING THE POSTS OF ALL THE USER IDS WHICH WERE COLLECTED
    extraction_userIDs = [str(value) for value in sampledf['userID']]
    #First empty the  collections
    replaceCollection(workflows['postsTimerange_new']['collections']['userIDs'], extraction_userIDs, API_TOKEN)
    #Lets run the workflow once again! - If everything is correct this returns a CSV file.
    postsJSON = executeWorkflow(workflows['postsTimerange_new']['workflowID'], API_TOKEN, "dedicated", 'csv', profileName, 500)
    #Executing a function to store this result in the data folder so nothing is lost
    
    ###storeJSON(postsJSON, profileName+"_followerProfile")
    if run == 'first':
        postsJSON.to_csv('../rawdata/{}_followerProfile.csv'.format(profileName)) #DELETE IF BACK TO JSON. DONT FORGET TO CHANGE workflowCall_postTimerange FUNCTION (NOT SET AT CSV)
    else:
        postsJSON.to_csv('../rawdata/{}_{}_followerProfile.csv'.format(profileName, run)) #DELETE IF BACK TO JSON. DONT FORGET TO CHANGE workflowCall_postTimerange FUNCTION (NOT SET AT CSV)
    print("FINISHED - Successfully created a follower profile for {}.".format(profileName))
    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Scraper to create Instagram follower Profiles.')
    parser.add_argument('--name', type=str, default=None, help='Profile Name to scrape.')
    parser.add_argument('--run', type=str, default='first', help='Are you going to create another profile for the company?')
    parser.add_argument('--followerLoc', type=str, default=None, help='Pinpoint the json file with follower names so we do not need to extract this anymore.')    
    #Adding the parser arguments as objects to the variable args.
    args = parser.parse_args()
    #Calling the main function.
    main(args.name, args.run, args.followerLoc, workflows, sessionIDs, API_TOKEN)

    