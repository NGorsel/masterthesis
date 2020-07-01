import requests
import json
import time
import urllib.request as ur
import pandas as pd
from samplesize import calculate_samplesize
from datetime import datetime
from collections import Counter

#---------------------- SINGLE API CALLS --------------------

def checkSessionID(sessionID, API_TOKEN, user_id='9623334065'):
    """This function very simply checks whether a session ID is working. It returns Falsee or True."""
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


def obtainUserJSON(profileName, sessionID, API_TOKEN):
    """Asks for a profileName and obtains all the JSON for one specific user"""
    r = requests.post(
        'https://stevesie.com/cloud/api/v1/endpoints/ea462d24-fa4f-4b36-ab01-1c908b021a8b/executions',
        headers={
            'Token': API_TOKEN, 
        },
        json={
            'inputs': {
                'username': profileName,
                'session_id': sessionID
            },
            'proxy': {
              'type': 'shared',
              'location': 'nyc',
            },
            'format': 'json'
        },
    )
    response_json = r.json()
    if response_json['object']['response']['status_code'] != 200:
        print("Obtaining UserJSON failed! Response code: {}".format(response_json['object']['response']['status_code']))
        return
    else:
        return response_json

def singleUserID(response_json):
    return response_json['object']['response']['response_json']['graphql']['user']['id'] 

def singleUserFollowers(response_json):
    return response_json['object']['response']['response_json']['graphql']['user']['edge_followed_by']['count']

#----------------------UPDATE COLLECTIONS --------------------

def updateCollection(collectionID, values, API_TOKEN, action, URL_BASE = 'https://stevesie.com/cloud/api/v1'):
    """This function uses as input a collectionID, the values you wish to add or remove to the collection, and the action 
    (remove or add). It prints the API json response which shows how many items there are currently in the collection."""
    auth_headers = {
        'Token': API_TOKEN
    }
    if type(values) != list:
        print("ERROR - Values may only consist of a list")
        return
    for value in values:
        if type(value) != str:
            print("ERROR - The values added to the collection must consist of strings!")
            return
    #All valid actions are listed. function is stopped when a non-valid action is given as input.
    valid_actions = ['add', 'remove']
    if action not in valid_actions:
        print("The action can only be either add or remove! not", action)
        return
    #The request we send to the collection
    r = requests.post(
    '{}/collections/{}'.format(URL_BASE, collectionID),
    json={
        'method': action,
        'items': values
    },
    headers=auth_headers,
    ).json()
    #This exception deals with the fact if we want to remove something from the collection while it is already empty.
    if 'errors' in r.keys():
        if r['errors'][0]['items'] == 'Blank.':
            print("INFO - Tried removing values from collection {}. However, it was already empty.".format(collectionID))
            return
        else:
            print("Unknown error at function updateCollection occured!")
            return
    #Very short script to make sure the printed output is a but better to look at.
    action_print = 'Added'
    if action == 'remove':
        action_print = 'Removed'
    print("INFO - {} {} values from collection {}. Current length: {}".format(action_print, len(values), collectionID, r['object']['count']))
    return


def replaceCollection(collectionID, values, API_TOKEN, URL_BASE = 'https://stevesie.com/cloud/api/v1'):
    """This function takes all the current values stored in a collection. It removes these values
    from the collection and enters new values in the collection which are provided"""
    current_collectionValues = showCollection(collectionID, API_TOKEN)
    #Here we remove all the current values in the collection
    updateCollection(collectionID, current_collectionValues, API_TOKEN, 'remove')
    #Adding the new values to the collection
    updateCollection(collectionID, values, API_TOKEN, 'add')
    print("INFO - Replaced collection:", collectionID)
    return


def showCollection(collectionID, API_TOKEN, URL_BASE = 'https://stevesie.com/cloud/api/v1'):
    """Simply return all the values which are stored in a collectionID."""
    auth_headers = {
        'Token': API_TOKEN
    }
    r = requests.get(
        '{}/collections/{}'.format(URL_BASE, collectionID),
        headers=auth_headers,
    ).json()
    collection_items = [item for item in r['object']['items']]
    return collection_items

#---------------------- EXECUTE WORKFLOW --------------------

def workflowCall(workflowID, API_TOKEN, proxyType, executionName, MRC, proxyLocation='nyc', URL_BASE = 'https://stevesie.com/cloud/api/v1'):
    """This function will start running a workflow. Be carefull executing this specific function!"""
    if proxyType not in ['dedicated', 'shared']:
        print("Workflow cancelled. Only proxy types shared and dedicated are allowed.")
    auth_headers = { 'Token': API_TOKEN }
    execution = requests.post(
        '{}/workflows/{}/executions'.format(URL_BASE, workflowID),
        json={
            'proxy': {
                'type': proxyType,
                'location': proxyLocation,
                },
            'output_aggregation_format' : "json",
            'maximum_requests_count' : MRC,
            'execution_name' : executionName,
            'send_completion_email': False,
            },
    headers=auth_headers,).json()
    return(execution)


def workflowCall_postTimerange(workflowID, API_TOKEN, proxyType, MIN_DATE, MAX_DATE, executionName, proxyLocation='nyc', URL_BASE = 'https://stevesie.com/cloud/api/v1'):
    """This function will start running a workflow. Be carefull executing this specific function!"""
    datetime(2012,4,1,0,0).timestamp()
    #Here we extract the epoch seconds for the MIN and MAX date
    min_date_timestamp = str(datetime.strptime(MIN_DATE, '%Y-%m-%d').timestamp())
    max_date_timestamp = str(datetime.strptime(MAX_DATE, '%Y-%m-%d').timestamp())

    if proxyType not in ['dedicated', 'shared']:
        print("Workflow cancelled. Only proxy types shared and dedicated are allowed.")
        return
    
    auth_headers = { 'Token': API_TOKEN }
    
    execution = requests.post(
        '{}/workflows/{}/executions'.format(URL_BASE, workflowID),
        json={
            'proxy': {
                'type': proxyType,
                'location': proxyLocation,
            },
            'execution_parameters': {
                'min_timestamp': min_date_timestamp,
                'max_timestamp': max_date_timestamp,
            },
            'output_aggregation_format' : "csv",
            'maximum_requests_count' : 10000,
            'execution_name' : executionName,
            'send_completion_email': False,
            },
    headers=auth_headers,).json()
    return(execution)



def executeWorkflow(workflowID, API_TOKEN, proxyType, format, executionName, MRC, URL_BASE = 'https://stevesie.com/cloud/api/v1'):
    """Executes a given workflow. Continousely provides the user with feedback about how the workflow is running
    and which data it is returning. At the end it provides the user with the workflow result in JSON format."""
              
    #Running a new workflow execution with the API function.
    if workflowID in ["ed8a59aa-b40a-497e-b20c-175109e15123"]: #Extract follower names
        workflowCall(workflowID, API_TOKEN, proxyType, executionName, MRC)
    elif workflowID in ["bfa05c12-f566-4368-8675-735a0dc5f6b9"]: #Extract posts of a collection of UserIDS
        workflowCall_postTimerange(workflowID, API_TOKEN, proxyType, "2019-01-01", "2020-01-01", executionName) 
    
    #Storing the executions we already have
    executionJSON = workflowExecutionsJSON(workflowID, API_TOKEN)
    executionNames = [execution['execution_name'] for execution in executionJSON['objects']]

    while executionName not in executionNames:
        print("INFO - New execution not yet discovered! Waiting Time: {} seconds.".format(seconds))
        time.sleep(5)
        executionNames = [execution['execution_name'] for execution in workflowExecutionsJSON(workflowID, API_TOKEN)['objects']]
        seconds += 5
    else:
        created_at_executionTimestamp = datetime.strptime(executionDetails(workflowExecutionsJSON(workflowID, API_TOKEN), executionName)['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ').timestamp()
        while datetime.now().timestamp() - created_at_executionTimestamp > 10800: # 0 is equal to 7200; somehow stevesie is two hours behind my time...
            print("INFO - Most recent workflow execution named {} occured more than 60minutes ago. Time to sleep 5sec.".format(executionName))
            time.sleep(5)
            created_at_executionTimestamp = datetime.strptime(executionDetails(workflowExecutionsJSON(workflowID, API_TOKEN), executionName)['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ').timestamp()
        else:
            print("INFO - New workflow execution found. Created {} seconds ago.".format(datetime.now().timestamp() - created_at_executionTimestamp))
            workflowExecutionID = executionDetails(workflowExecutionsJSON(workflowID, API_TOKEN), executionName)['id']

    #We found a new execution ID. Now make sure to keep it updating for new results.
    execution_result_IDS = []
    
    new_execution_details = executionDetails_ID(workflowExecutionsJSON(workflowID, API_TOKEN), workflowExecutionID) 
    workflow_execution_second = 0 

    while new_execution_details['completed_at'] == None:
        print("INFO - Workflow execution not finished yet. Waiting Time: {} minutes.".format(workflow_execution_second))
        time.sleep(30)
        
        #Updating whether the running execution has a new result. If it does we print the running code.
        new_execution_result_IDS = workflowExecutionIDS(new_execution_details['results'])
        for value in new_execution_result_IDS:
            if value not in execution_result_IDS:
                #Using the new_execution_details function to define the code of the new found execution ID
                value_code = executionResult_code(new_execution_details, value)
                print('UPDATE - A new result was received with status code: {}'.format(value, value_code))
                execution_result_IDS.append(value)           
        #Update timer and the execution details so we can discover new results! :-)
        workflow_execution_second += 0.5
        new_execution_details = executionDetails_ID(workflowExecutionsJSON(workflowID, API_TOKEN), workflowExecutionID) 

    else:
        #The workflow execution is finished. Lets wait 10 more seconds and just take the last result. This should contain the final JSON or CSV file.
        print('INFO - Workflow execution finished! Extracting results ... This will take 10 seconds.')
        time.sleep(10)
        result_location = [value['url'] for value in new_execution_details['results']][0]

      # if workflowID in ["ed8a59aa-b40a-497e-b20c-175109e15123"]: #Extract follower names
      #      #Printing the final found even though the workflow is finished
      #      
      #      
      #      if len(new_execution_result_IDS) > 1:
      #          #Reversing the list so the final result is at the back of the list.
      #          final_execution_result_ID = new_execution_result_IDS[0]
      #          new_execution_result_IDS = new_execution_result_IDS[1::].reverse()
      #      else:
      #          final_execution_result_ID = new_execution_result_IDS[0]
      #          new_execution_result_IDS = []
      #      
      #      try:
      #          for value in new_execution_result_IDS:
      #              if value not in execution_result_IDS:
      #                  #Using the new_execution_details function to define the code of the new found execution ID
      #                  value_code = executionResult_code(new_execution_details,value)
      #                  print("UPDATE - New execution result {}. Code: {}".format(value, value_code))
      #                  execution_result_IDS.append(value) 
      #      except TypeError:
      #          print('INFO - Attention: somehow no new results were found. This may indicate an error.')
      #
      #      #Lastly printing the location of the final result file and returning the JSON which is found in that link.
      #      result_location = [value['url'] for value in new_execution_details['results'] if value['id'] == final_execution_result_ID][0]
      #      print("UPDATE - The workfow execution is finished. Final results are stored in the following link: {}".format(result_location))
      #      
        if format == 'csv':
            datadf = pd.read_csv(result_location)
            return datadf
            
        response = ur.urlopen(result_location)
        data = json.loads(response.read())
        return data

   
    

#---------------------- SHOW RESULTS --------------------

def executionDetails(response_json, execution_name):
    """Once a new workflow execution is found. This function obtains all JSON data
    of that specific workflow execution. Used to continouesely update the terminal."""
    found_execution = [value for value in response_json['objects'] if value['execution_name'] == execution_name]
    if len(found_execution) == 1:
        return found_execution[0]
    else:
        print('IMPORTANT - We found multiple executions with ID {}. We picked most recent one!'.format(execution_name))
        return found_execution[0]

def executionDetails_ID(response_json, execution_id):
    """Once a new workflow execution is found. This function obtains all JSON data
    of that specific workflow execution. Used to continouesely update the terminal."""
    found_execution = [value for value in response_json['objects'] if value['id'] == execution_id]
    if len(found_execution) == 1:
        return found_execution[0]
    else:
        print('ERROR - We found multiple workflow executions with ID {}. This should not be possible but we continued using the most recent one!'.format(execution_id))
        return found_execution[0]

def workflowExecutionsJSON(workflowID, API_TOKEN, URL_BASE = 'https://stevesie.com/cloud/api/v1'):
    """Returns all the results of one specific workflow ID."""
    auth_headers = { 'Token': API_TOKEN }
    response_json = requests.get(
    '{}/workflows/{}/executions'.format(URL_BASE, workflowID),
    headers=auth_headers,).json()
    return response_json


def workflowExecutionIDS(response_json):
    """Searches the JSON file of one specific workflow to discover all
    the different executions. Used to find the new execution."""
    return [value['id'] for value in response_json]


def executionUpdates(old_executionIDS, new_executionIDS):
    """Checks whether new execution IDS have ocurred. If this is the case
    it prints the details of that specific workflow as output. (response_code)"""
    new_executionIDS = [x for x in new_executionIDS if x not in old_executionIDS]    
    if len(new_executionIDS) == 0:
        return False
    elif len(new_executionIDS) == 1:
        return new_executionIDS[0]
    else:
        print('ERROR - Somehow we discovered multiple new execution IDs!')
        print(new_executionIDS)
        return


def executionResult_code(JSON, ID):
    """Uses output of the executionUpdates function to obtain the response_code
    of one specific result of a running workflow execution."""
    link = [value['url'] for value in JSON['results'] if value['id'] == ID]
    if len(link) != 1:
        print('Somehow we obtained zero or less than one link: {}'.format(link))
        return
    else:
        if link[0].endswith('.csv'):
            return ".CSV file, no status code provided."
        response = ur.urlopen(link[0])
        data = json.loads(response.read())
        return data['response']['status_code']


def storeJSON(data, filename):
    """Function takes JSON format data as input and stores it as a JSON file in the data folder."""
    with open('data/' + filename + '.json', 'w') as f:
        json.dump(data, f)
    print('INFO - Stored obtained data under the following location: {}'.format('data/' + filename + '.json'))
    return 

#---------------------- EDIT RESULTS OF WORKFLOW --------------------

def createFollowerdf(results):
    """Creates a dataframe from the results. Only keeps the UserID, username and private."""
    person_dataframe = []
    for person in results:
        userID = person['response']['node.id']
        userName = person['response']['node.username']
        userPrivate = person['response']['node.is_private']
        #Appending everything to the inner list
        person_dataframe.append([userID, userName, userPrivate])
    #Lets create the dataframe
    df = pd.DataFrame(person_dataframe)
    df.columns = ['userID', 'username', 'private']
    #Delete double userIDs and return it as result.
    return df.drop_duplicates(subset='userID').reset_index(drop=True)



def obtainSample(df, population):
    """Takes dataframe created by the createFollowerdf function. Select enough rows of the dataframe until the given
    confidence level and confidence intervals are obtained based on the Instagram profile numer of followers."""
    #Only select followers with private on false; otherwise we cant obtain their tweets.
    sample_size = calculate_samplesize(population) + 200 #DELETE THIS ADDS 200 EXTRA TO SAMPLE SIZE!!
    df = df.loc[df['private'] == False]
    
    if len(df) < sample_size:
        print("ALERT - Created sample size of {} instead of {}. Not enough profiles with private settings on False.".format(len(df), sample_size))
        sample_size = len(df)
    #Calculates how much percentage of the dataframe is the samplesize and takes this fraction.
    fraction = sample_size / len(df)
    df_percent = df.sample(frac=fraction)
    print("INFO - randomly created a sample size of {} followers.".format(sample_size))
    return df_percent

 

#API_TOKEN = "2909aaa7-b017-45c5-b96a-314bb8aa325c"
#print(checkSessionID('25864241221%3A86BVZymXHPbuDp%3A17', API_TOKEN, user_id='9623334065'))