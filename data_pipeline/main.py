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
API_TOKEN = "2909aaa7-b017-45c5-b96a-314bb8aa325c"

auth_headers = {
  'Token': API_TOKEN,
}

#known userIDs
userIDs = {
    "ikeanederland" : "289542609",
    "joerivandermeer" : "919159490",
    "broederschap_der_kruisridders" : "9623334065",
    "myronvg" : "40032967",
    "zinzzi" : "5903508"
}


#Session IDs of three of my accounts.
sessionIDs = {
#"slushpuppy112358" : "25088326271%3AYOUQLjsMbReZG7%3A4",
"dragonsden112358" : "25126372963%3AcPu7E7TCUB8tBh%3A1",
"Lycamobile112358" :"25713281404%3ANVM8xGdxaPr1Se%3A11",
#"openidaging" : "25841755182%3AJHPEccikN0Cpjw%3A10",
#"unmovablehis" : "26403210604%3AziQol4ThUsqeei%3A27",
"dormanthitter" : "26409601578%3A4IEsGfuSWw6MWi%3A28",
#"aftermathbeneficent" : "26197293736%3ANIFMJNu5TNZe4y%3A14",
#"farigaigbapser" : "26230456483%3AB8LZchWeNBtne4%3A18",
#"gentilegalvanising" : "25994207495%3AIEmCofLFz9i53T%3A3",
#"poodunlin" : "26210450746%3AjnAfz3imUb8jWZ%3A23",
#"havenergonomic" : "25832908687%3ANRhMglKqBXW5iy%3A6",
#"grainsgilldeceiveerx" : "26223202227%3Ae064HdXF0AfA3D%3A15",
#"surveyskoardser" : "26204950382%3A63y1ZI2qA7QXWF%3A24",
#"fierycollecteder" : "25850539344%3AyAZJ0dHa1BBqJt%3A14",
#"exploretidingr" : "26217044169%3AY7uv2WX8waWhSM%3A2",
"punctuatebicycle" : "25864241221%3A86BVZymXHPbuDp%3A17"
#"tripwirereuse": "26205214104%3AD9LjL4k82O92uE%3A1"

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
            with open('data/{}_second_followers.json'.format(profileName)) as json_file:
                userFollowersJSON = json.load(json_file)
        elif followerLoc:
            with open('data/{}'.format(followerLoc)) as json_file:
                userFollowersJSON = json.load(json_file)
        else:
            with open('data/{}_followers.json'.format(profileName)) as json_file:
                userFollowersJSON = json.load(json_file)

        stored_nameDict = createFollowerdf(userFollowersJSON)
        #I only want to extract the usernames which have private settings on False
        nonPrivate_nameDict = stored_nameDict.loc[stored_nameDict['private'] == False]
        # All IDS we extracted, now we just have to remove the names we already scraped.
        all_IDS = [value for value in nonPrivate_nameDict['username']]
        # Now we take a look at the follower profile we already created. We do not want
        # to extract posts from these usernames again!
        if run == 'fourth':
            post_df_1 = pd.read_csv('data/{}_followerProfile.csv'.format(profileName))
            post_df_2 = pd.read_csv('data/{}_second_followerProfile.csv'.format(profileName))
            post_df_3 = pd.read_csv('data/{}_third_followerProfile.csv'.format(profileName))
            extracted_IDS_1 = [value for value in [value for value in set(post_df_1['data.user.edge_owner_to_timeline_media.edges.node.owner.username'])]]
            extracted_IDS_2 = [value for value in [value for value in set(post_df_2['data.user.edge_owner_to_timeline_media.edges.node.owner.username'])]]
            extracted_IDS_3 = [value for value in [value for value in set(post_df_3['data.user.edge_owner_to_timeline_media.edges.node.owner.username'])]]
            extracted_IDS = extracted_IDS_1 + extracted_IDS_2 + extracted_IDS_3
        elif run == 'third':
            post_df_1 = pd.read_csv('data/{}_followerProfile.csv'.format(profileName))
            post_df_2 = pd.read_csv('data/{}_second_followerProfile.csv'.format(profileName))
            extracted_IDS_1 = [value for value in [value for value in set(post_df_1['data.user.edge_owner_to_timeline_media.edges.node.owner.username'])]]
            extracted_IDS_2 = [value for value in [value for value in set(post_df_2['data.user.edge_owner_to_timeline_media.edges.node.owner.username'])]]
            extracted_IDS = extracted_IDS_1 + extracted_IDS_2
        elif run == 'second':
            post_df = pd.read_csv('data/{}_followerProfile.csv'.format(profileName))
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
        #Using three function to first create a dataframe, than calculate sample size and
        #thirdly select n (sample size) profiles which have their private settings off.
        ####with open('data/{}_followers.json'.format(profileName)) as json_file:
        ####    userFollowersJSON = json.load(json_file)
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
        postsJSON.to_csv('data/{}_followerProfile.csv'.format(profileName)) #DELETE IF BACK TO JSON. DONT FORGET TO CHANGE workflowCall_postTimerange FUNCTION (NOT SET AT CSV)
    else:
        postsJSON.to_csv('data/{}_{}_followerProfile.csv'.format(profileName, run)) #DELETE IF BACK TO JSON. DONT FORGET TO CHANGE workflowCall_postTimerange FUNCTION (NOT SET AT CSV)
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

    