import json
import requests
import ipywidgets as widgets
from IPython.display import display
import pandas as pd
import warnings

warnings.filterwarnings('ignore')

# API details
serverIp = '172.16.1.24'
serverPort = '8111'
authId = "c2FuZGxpbmtfYXBpOlRXQ2FwaTIwMjQ="
headers = {"accept": "application/ld+json", "authorization": f"Basic {authId}"}

# Get workspaces
call = '/osmc/workspaces?includeBody=True'
url = f'https://{serverIp}:{serverPort}{call}'
resp_ws = requests.get(url, headers=headers, verify=False)
workspaces = resp_ws.json()

# Create dictionaries for workspace IDs and names
workspaceIds = {i: workspaces["ldp:contains"][i][0]['@id'] for i in range(len(workspaces["ldp:contains"]))}
workspaceNames = {i: workspaces["ldp:contains"][i][1]["dcterms:title"] for i in range(len(workspaces["ldp:contains"]))}

# Define a function to handle dropdown events
def dropdown_eventhandler(change):
    print(change.new)

# Create a dropdown list of available workspaces
ws = widgets.Dropdown(options=workspaceNames.values(), description='Workspaces:')
ws.observe(dropdown_eventhandler, names='value')

# Display the combobox
display(ws)

# Get the selected workspace ID
wsIndex = list(filter(lambda x: workspaceNames[x] == ws.value, range(len(workspaceNames))))
workspaceId = workspaceIds[wsIndex[0]] if wsIndex else "bee3d988-bcc4-463a-9c69-e2d5dcd6da27"

# List projects within the selected workspace
call = f'/osmc/workspaces/{workspaceId}/resources'
url = f'https://{serverIp}:{serverPort}{call}'
resp_projects = requests.get(url, headers=headers, verify=False)
projectsList = resp_projects.json()
projectsUidList = projectsList[1]['kerml:resources']

# Create a dictionary of project details
projectsData = {}
for i in range(len(projectsUidList)):
    resourceId = projectsUidList[i]['@id']
    call = f'/osmc/workspaces/{workspaceId}/resources/{resourceId}'
    url = f'https://{serverIp}:{serverPort}{call}'
    resp_projects = requests.get(url, headers=headers, verify=False)
    projectsData[i] = resp_projects.json()

# Create dictionaries for project IDs and names
projectIds = {i: projectsData[i]['@base'].split("/")[7] for i in range(len(projectsData))}
projectNames = {i: projectsData[i]['metadata']['name'].split(".")[0] for i in range(len(projectsData))}

# Create a dropdown list of available projects
prj = widgets.Dropdown(options=projectNames.values(), description='Projects:')
prj.observe(dropdown_eventhandler, names='value')

# Display the combobox
display(prj)

# Get the selected project ID
prjIndex = list(filter(lambda x: projectNames[x] == prj.value, range(len(projectNames))))
projectId = projectIds[prjIndex[0]] if prjIndex else "a9aeef9b-8353-4c50-9458-a3467d7f2628"

# Fetch the revision list
call = f'/osmc/workspaces/{workspaceId}/resources/{projectId}/revisions'
url = f'https://{serverIp}:{serverPort}{call}'
resp_revList = requests.get(url, headers=headers, verify=False)
revisionList = resp_revList.json()

# Initialize a DataFrame to store elements from all versions
df = pd.DataFrame(columns=["Version Number", "Element ID", "Element Name", "Documentation"])

# Iterate through each version and fetch elements
for revision in revisionList:
    sourceRevision = 1
    targetRevision = revision
    call = f'/osmc/workspaces/{workspaceId}/resources/{projectId}/revisiondiff?source={sourceRevision}&target={targetRevision}'
    url = f'https://{serverIp}:{serverPort}{call}'
    resp_elementList = requests.get(url, headers=headers, verify=False)
    elementList_json = resp_elementList.json().get('added', [])

    # Directly use elementList_json as it is a list of element IDs
    element_ids = elementList_json
    #print(element_ids)

    # Fetch elements for this version
    call = f'/osmc/resources/{projectId}/elements'
    url = f'https://{serverIp}:{serverPort}{call}'
    headers = {"accept": "application/ld+json", "Content-Type": "text/plain", "authorization": f"Basic {authId}"}
    elementList_str = ",".join(element_ids)
    resp_elementListData = requests.post(url, headers=headers, verify=False, data=elementList_str)
    elementListData = resp_elementListData.json()

    #print(elementListData)

    # Temporary DataFrame to store data for this version
    temp_df = pd.DataFrame(columns=["Version Number", "Element ID", "Element Name", "Documentation"])

    # Extract data for each element and add to temporary DataFrame
    for element_id in element_ids:
        element_data = elementListData.get(element_id, {}).get('data', [{}])
        #print(element_data)
        if element_data:
            ownersId = element_data[1].get('kerml:owner', {}).get('@id', 'Unknown')
            print(ownersId)
        
            """ 
            ownersName = elementListData.get(ownersId, {}).get('data', [{}])[1].get('kerml:name', 'null') if ownersId != 'Unknown' else 'null'
            if not ownersName:
                ownersName = 'null'            
            print(ownersName)
            """
            body = element_data[1].get("kerml:esiData", {}).get("body", "")
            print(body)
            temp_df = pd.concat([temp_df, pd.DataFrame({"Version Number": [targetRevision], "Element ID": [element_id], "Documentation": [body]})])

    # Concatenate temporary DataFrame to the main DataFrame
    df = pd.concat([df, temp_df], ignore_index=True)

# Display the DataFrame with elements from all versions
print(df)

"""
Output:

import json
import requests
import ipywidgets as widgets
from IPython.display import display
import pandas as pd
import warnings

warnings.filterwarnings('ignore')

# API details
serverIp = '172.16.1.24'
serverPort = '8111'
authId = "c2FuZGxpbmtfYXBpOlRXQ2FwaTIwMjQ="
headers = {"accept": "application/ld+json", "authorization": f"Basic {authId}"}

# Get workspaces
call = '/osmc/workspaces?includeBody=True'
url = f'https://{serverIp}:{serverPort}{call}'
resp_ws = requests.get(url, headers=headers, verify=False)
workspaces = resp_ws.json()

# Create dictionaries for workspace IDs and names
workspaceIds = {i: workspaces["ldp:contains"][i][0]['@id'] for i in range(len(workspaces["ldp:contains"]))}
workspaceNames = {i: workspaces["ldp:contains"][i][1]["dcterms:title"] for i in range(len(workspaces["ldp:contains"]))}

# Define a function to handle dropdown events
def dropdown_eventhandler(change):
    print(change.new)

# Create a dropdown list of available workspaces
ws = widgets.Dropdown(options=workspaceNames.values(), description='Workspaces:')
ws.observe(dropdown_eventhandler, names='value')

# Display the combobox
display(ws)

# Get the selected workspace ID
wsIndex = list(filter(lambda x: workspaceNames[x] == ws.value, range(len(workspaceNames))))
workspaceId = workspaceIds[wsIndex[0]] if wsIndex else "bee3d988-bcc4-463a-9c69-e2d5dcd6da27"

# List projects within the selected workspace
call = f'/osmc/workspaces/{workspaceId}/resources'
url = f'https://{serverIp}:{serverPort}{call}'
resp_projects = requests.get(url, headers=headers, verify=False)
projectsList = resp_projects.json()
projectsUidList = projectsList[1]['kerml:resources']

# Create a dictionary of project details
projectsData = {}
for i in range(len(projectsUidList)):
    resourceId = projectsUidList[i]['@id']
    call = f'/osmc/workspaces/{workspaceId}/resources/{resourceId}'
    url = f'https://{serverIp}:{serverPort}{call}'
    resp_projects = requests.get(url, headers=headers, verify=False)
    projectsData[i] = resp_projects.json()

# Create dictionaries for project IDs and names
projectIds = {i: projectsData[i]['@base'].split("/")[7] for i in range(len(projectsData))}
projectNames = {i: projectsData[i]['metadata']['name'].split(".")[0] for i in range(len(projectsData))}

# Create a dropdown list of available projects
prj = widgets.Dropdown(options=projectNames.values(), description='Projects:')
prj.observe(dropdown_eventhandler, names='value')

# Display the combobox
display(prj)

# Get the selected project ID
prjIndex = list(filter(lambda x: projectNames[x] == prj.value, range(len(projectNames))))
projectId = projectIds[prjIndex[0]] if prjIndex else "a9aeef9b-8353-4c50-9458-a3467d7f2628"

# Fetch the revision list
call = f'/osmc/workspaces/{workspaceId}/resources/{projectId}/revisions'
url = f'https://{serverIp}:{serverPort}{call}'
resp_revList = requests.get(url, headers=headers, verify=False)
revisionList = resp_revList.json()

# Initialize a DataFrame to store elements from all versions
df = pd.DataFrame(columns=["Version Number", "Element ID", "Element Name", "Documentation"])

# Iterate through each version and fetch elements
for revision in revisionList:
    sourceRevision = 1
    targetRevision = revision
    call = f'/osmc/workspaces/{workspaceId}/resources/{projectId}/revisiondiff?source={sourceRevision}&target={targetRevision}'
    url = f'https://{serverIp}:{serverPort}{call}'
    resp_elementList = requests.get(url, headers=headers, verify=False)
    elementList_json = resp_elementList.json().get('added', [])

    # Directly use elementList_json as it is a list of element IDs
    element_ids = elementList_json
    #print(element_ids)

    # Fetch elements for this version
    call = f'/osmc/resources/{projectId}/elements'
    url = f'https://{serverIp}:{serverPort}{call}'
    headers = {"accept": "application/ld+json", "Content-Type": "text/plain", "authorization": f"Basic {authId}"}
    elementList_str = ",".join(element_ids)
    resp_elementListData = requests.post(url, headers=headers, verify=False, data=elementList_str)
    elementListData = resp_elementListData.json()

    #print(elementListData)

    # Temporary DataFrame to store data for this version
    temp_df = pd.DataFrame(columns=["Version Number", "Element ID", "Element Name", "Documentation"])

    # Extract data for each element and add to temporary DataFrame
    for element_id in element_ids:
        element_data = elementListData.get(element_id, {}).get('data', [{}])
        #print(element_data)
        if element_data:
            ownersId = element_data[1].get('kerml:owner', {}).get('@id', 'Unknown')
            print(ownersId)
        
            """ 
            ownersName = elementListData.get(ownersId, {}).get('data', [{}])[1].get('kerml:name', 'null') if ownersId != 'Unknown' else 'null'
            if not ownersName:
                ownersName = 'null'            
            print(ownersName)
            #Get out of index error
            """
            body = element_data[1].get("kerml:esiData", {}).get("body", "")
            print(body)
            temp_df = pd.concat([temp_df, pd.DataFrame({"Version Number": [targetRevision], "Element ID": [element_id], "Documentation": [body]})])

    # Concatenate temporary DataFrame to the main DataFrame
    df = pd.concat([df, temp_df], ignore_index=True)

# Display the DataFrame with elements from all versions
print(df)

"""
Output:

Dropdown(description='Workspaces:', options=('S4',), value='S4')
Dropdown(description='Projects:', options=('valueProperties',), value='valueProperties')
3286e597-8a26-4cbe-af21-54897682582e
hello
de37b3ee-ad71-4df1-9e88-a3752b257d4d

7a4b4734-7acb-4556-b64f-4b9c39e1ef5d
hi table doc
ee05b1cd-47ee-44e5-8285-5f27cbecccd7

94aa294f-c0e1-4c87-8c01-3def5bcdcf25

1a4a29e5-3273-4566-9d53-3c65d579be2b

94aa294f-c0e1-4c87-8c01-3def5bcdcf25
block1 doc nect version for monday
94aa294f-c0e1-4c87-8c01-3def5bcdcf25

35c07848-c6e7-4dd2-9cdd-1d7a0a774fda
block 2 docu for tesing at august 5
7a4b4734-7acb-4556-b64f-4b9c39e1ef5d

7a4b4734-7acb-4556-b64f-4b9c39e1ef5d

7a4b4734-7acb-4556-b64f-4b9c39e1ef5d

94aa294f-c0e1-4c87-8c01-3def5bcdcf25

7a4b4734-7acb-4556-b64f-4b9c39e1ef5d

35c07848-c6e7-4dd2-9cdd-1d7a0a774fda

16861878-eb2a-4c77-b50f-cee26691b617

7a4b4734-7acb-4556-b64f-4b9c39e1ef5d

ee05b1cd-47ee-44e5-8285-5f27cbecccd7

65561fb4-d709-4a7a-ad7f-dbda08b16c43

7a4b4734-7acb-4556-b64f-4b9c39e1ef5d

21ca863a-28d0-42a5-ae29-61d8b889a181

7a4b4734-7acb-4556-b64f-4b9c39e1ef5d

3286e597-8a26-4cbe-af21-54897682582e

7a4b4734-7acb-4556-b64f-4b9c39e1ef5d

7a4b4734-7acb-4556-b64f-4b9c39e1ef5d

7a4b4734-7acb-4556-b64f-4b9c39e1ef5d

21ca863a-28d0-42a5-ae29-61d8b889a181

7a4b4734-7acb-4556-b64f-4b9c39e1ef5d

44626d6a-333e-46e3-abcc-152ebda613e4
block one operation
7a4b4734-7acb-4556-b64f-4b9c39e1ef5d

21ca863a-28d0-42a5-ae29-61d8b889a181

21ca863a-28d0-42a5-ae29-61d8b889a181

6c4e12c0-ae80-470a-b4b9-e1b682f36268

7a4b4734-7acb-4556-b64f-4b9c39e1ef5d

ee05b1cd-47ee-44e5-8285-5f27cbecccd7

7a4b4734-7acb-4556-b64f-4b9c39e1ef5d

60bf327b-cf50-4add-ad65-8a29d0b3d422

7a4b4734-7acb-4556-b64f-4b9c39e1ef5d

7a4b4734-7acb-4556-b64f-4b9c39e1ef5d

21ca863a-28d0-42a5-ae29-61d8b889a181

7a4b4734-7acb-4556-b64f-4b9c39e1ef5d

fbbb75aa-aa3e-4c6a-aa2a-fe6d38e9485e

7a4b4734-7acb-4556-b64f-4b9c39e1ef5d

94aa294f-c0e1-4c87-8c01-3def5bcdcf25

7a4b4734-7acb-4556-b64f-4b9c39e1ef5d

3286e597-8a26-4cbe-af21-54897682582e
hello
de37b3ee-ad71-4df1-9e88-a3752b257d4d

7a4b4734-7acb-4556-b64f-4b9c39e1ef5d
hi table doc
ee05b1cd-47ee-44e5-8285-5f27cbecccd7

94aa294f-c0e1-4c87-8c01-3def5bcdcf25

1a4a29e5-3273-4566-9d53-3c65d579be2b

94aa294f-c0e1-4c87-8c01-3def5bcdcf25
block1 doc nect version for monday
94aa294f-c0e1-4c87-8c01-3def5bcdcf25

35c07848-c6e7-4dd2-9cdd-1d7a0a774fda
block 2 docu for tesing at august 5
7a4b4734-7acb-4556-b64f-4b9c39e1ef5d

7a4b4734-7acb-4556-b64f-4b9c39e1ef5d

7a4b4734-7acb-4556-b64f-4b9c39e1ef5d

94aa294f-c0e1-4c87-8c01-3def5bcdcf25

7a4b4734-7acb-4556-b64f-4b9c39e1ef5d

35c07848-c6e7-4dd2-9cdd-1d7a0a774fda

16861878-eb2a-4c77-b50f-cee26691b617

7a4b4734-7acb-4556-b64f-4b9c39e1ef5d

ee05b1cd-47ee-44e5-8285-5f27cbecccd7

65561fb4-d709-4a7a-ad7f-dbda08b16c43

7a4b4734-7acb-4556-b64f-4b9c39e1ef5d

21ca863a-28d0-42a5-ae29-61d8b889a181

7a4b4734-7acb-4556-b64f-4b9c39e1ef5d

3286e597-8a26-4cbe-af21-54897682582e

7a4b4734-7acb-4556-b64f-4b9c39e1ef5d

7a4b4734-7acb-4556-b64f-4b9c39e1ef5d

7a4b4734-7acb-4556-b64f-4b9c39e1ef5d

Traceback (most recent call last):
  File "/home/sandlink/Documents/Cameo/RestAPI/Element_Documentation/pullFromSpecificversioninCmaeo.py", line 112, in <module>
    ownersId = element_data[1].get('kerml:owner', {}).get('@id', 'Unknown')
AttributeError: 'str' object has no attribute 'get'

"""
