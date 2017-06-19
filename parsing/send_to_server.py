import requests
import json

def server_post_data(seqnum, temp, light, message):
    # location
    url = 'http://localhost:3000/add_data'
    # print("HERE")
    # build data
    data = {}
    data['xvalue'] = seqnum
    data['temp'] = temp
    data['light'] = light
    data['message'] = message.rstrip("\u0000")  # remove blank information
    data_json = json.dumps(data)

    #build header
    # None currently    --> headers={}
    # TODO: include authorization information

    resp = requests.post(url, json=data)
    #print(resp)    # DEBUG
