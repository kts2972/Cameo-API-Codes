import json
import requests
import ipywidgets as widgets
from IPython.display import display
import pandas as pd
import warnings

warnings.filterwarnings('ignore')

# API details
serverIp = #twc server ip
serverPort = '8111'
authId = #Rest API Auth ID
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

    # Fetch elements for this version
    call = f'/osmc/resources/{projectId}/elements'
    url = f'https://{serverIp}:{serverPort}{call}'
    headers = {"accept": "application/ld+json", "Content-Type": "text/plain", "authorization": f"Basic {authId}"}
    elementList_str = ",".join(element_ids)
    resp_elementListData = requests.post(url, headers=headers, verify=False, data=elementList_str)
    elementListData = resp_elementListData.json()

    # Extract data for each element and add to DataFrame
    for element_id in element_ids:
        element_data = elementListData.get(element_id, {}).get('data', [{}])
        if element_data:
            ownersId = element_data[1].get('kerml:owner', {}).get('@id', 'Unknown')
            ownersName = elementListData.get(ownersId, {}).get('data', [{}])[1].get('kerml:name', 'Unknown')
            body = element_data[1].get("kerml:esiData", {}).get("body", "")
            #change to concate
            #df = df.append({"Version Number": targetRevision, "Element ID": element_id, "Element Name": ownersName, "Documentation": body}, ignore_index=True)

# Display the DataFrame with elements from all versions
print(df)

"""
Error:

3286e597-8a26-4cbe-af21-54897682582e
de37b3ee-ad71-4df1-9e88-a3752b257d4d
7a4b4734-7acb-4556-b64f-4b9c39e1ef5d
ee05b1cd-47ee-44e5-8285-5f27cbecccd7
Traceback (most recent call last):
  File "/home/sandlink/Documents/pullFromSpecificversioninCmaeo.py", line 105, in <module>
    ownersName = elementListData[ownersId]['data'][1]['kerml:name']
KeyError: 'ee05b1cd-47ee-44e5-8285-5f27cbecccd7'


This ID exists in the element_ids, but the error message shows that 

"""
