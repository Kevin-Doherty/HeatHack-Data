import requests
import pandas as pd
import os
import shutil
from datetime import datetime, timedelta


dataTimeNow = datetime.today().strftime('%Y%m%d_%H%M%S')

# Get the channel_id for the ThingSpeak API from the venueKeys
baseDirectory = os.path.dirname(__file__)

venueKeysPath = os.path.join(baseDirectory, 'venue-keys.csv')

try:
    venueKeys = pd.read_csv(venueKeysPath, dtype={'channel_id':str})
    print(venueKeys)
except Exception as e: 
    print("Error getting venue-key data from file: ", str(e))

# Drop all entries that don't have a channel id - these are standalone and handled separately.
venueKeys = venueKeys.dropna(subset=['channel_id'])
print(venueKeys)

# Extract Channel Ids for the API Call 
deviceChannelIds = venueKeys['channel_id']

# make sure indexes pair with number of rows
venueKeys.reset_index()  


for deviceIndex, deviceRow in venueKeys.iterrows() :

    filePath = os.path.join(baseDirectory, 'deviceData', deviceRow['sensor_MAC'] + '.csv')
    params = ''
    
    # Load existing data file if it exists and get the last timestamp
    try:
        existingData = pd.read_csv(filePath)
        existingData['timestamp'] = existingData['timestamp'] .str.replace('T',' ')
        # Z signifies UTC +0 - does it also consider daylight savings?
        existingData['timestamp'] = existingData['timestamp'] .str.replace('Z','')
        lastTimestampString = existingData.iloc[-1]['timestamp']
        lastTimestamp = datetime.strptime(lastTimestampString, '%Y-%m-%d %H:%M:%S')
        lastTimestampDelta = (lastTimestamp + timedelta(seconds=1)).strftime('%Y-%m-%d %H:%M:%S')

        params = f'?start={lastTimestampDelta}'
        print(f'Getting data from {lastTimestampDelta} onwards')

    except Exception as e:
        # Set 'dawn of time' value to bring back all data from sensors deployment
        params = '?start={\'2022-01-01 00:00:00\'}'
        print('No existing timestamp. Getting all data. ' + str(e))
    

    print(deviceRow['channel_id'])
    thisChannelID = deviceRow['channel_id']
    try:
        response = requests.get(f'https://api.thingspeak.com/channels/{thisChannelID}/feeds.json{params}');
    except Exception as e:
        print("Error getting device data: ", str(e))

    
    responseRaw = response.json()['feeds']
    responseDataFrame = pd.json_normalize(responseRaw)
    if (responseDataFrame.size > 0) : 
        responseDataFrame.columns = ["timestamp", "entry_id", "temperature", "rh", "voltage"]

        print('Adding new data to file: \n')
        print(responseDataFrame)
        responseCSV = responseDataFrame.to_csv()
        
        #filePath = os.path.join(baseDirectory, 'thermal-monitoring', 'deviceData', deviceRow['sensor_MAC'] + '.csv')

        try:
            responseDataFrame.to_csv(filePath, mode='a', index=False, header=not os.path.exists(filePath))
        except Exception as e:
            print("Error writing device data to file: ", str(e))
    else:
        print(f"No new data for sensor {deviceRow['channel_id']}.")
    


#Write to run log.


