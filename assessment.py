# -*- coding: utf-8 -*-
"""
Created on Sun Nov 22 03:15:30 2020

@author: Gabriel
Official implementation for parallel score assessment given
"""

#import the necessary Libraries
import json
import requests 
from flask import Flask, request, Response, jsonify
from retry import retry
#from tenacity import retry
app = Flask(__name__)


@retry( tries=2, delay=30) 
@app.route('/create-user', methods=['POST'])
def create_user():
    """
   
    Method creates a new user by posting a Json request
    
    Parameters
    ----------
    None

    Returns
    -------
    str
        Flask response

    """
    request_data = request.get_json()
    user_data = {
        "username": request_data["username"],
        "first_name": request_data["first_name"],
        "last_name": request_data["last_name"],
        "password": request_data["password"],
        "source": request_data["source"],
        "role": request_data["role"]
        }
    
    response = requests.post("http://ec2-3-95-53-126.compute-1.amazonaws.com:3700/signup/form", data = user_data)
    return response.json()



@retry( tries=2, delay=30)
@app.route('/<userNonce>/<userId>/update-account', methods=['POST'])
def update_account(userNonce, userId):

    request_data = request.get_json()
    update= {
        "update": {
            "first_name": request_data["first_name"],
            "last_name": request_data["last_name"],
            
        }
    }
    response = requests.post("http://ec2-3-95-53-126.compute-1.amazonaws.com:3700/profile/update/"+userNonce+"/"+userId, json=update)
    return response.json()




@retry(tries=2, delay=30)
@app.route('/login-user', methods=['POST'])
def login_user():

    
    

    """
   
    Logs the user in with username and password
    
    Parameters
    ----------
    None

    Returns
    -------
    str
        Flask response

    """

    request_data = request.get_json()
    user_data = {
        "username": request_data["username"],
        "password": request_data["password"],
        }
    
    
    
    response = requests.post("http://ec2-3-95-53-126.compute-1.amazonaws.com:3700/login/user", data = user_data)
    
    #print( response.json())

    return response.json()
    #raise ConnectionError
    


@retry( tries=2, delay=30) 
@app.route('/<userId>/logout-user', methods=['PUT'])
def logout_user(userId):

    response = requests.put('http://ec2-3-95-53-126.compute-1.amazonaws.com:3700/logout/user/' + userId )
    return response.json()


#@retry( tries=2, delay=3) 
@app.route('/<userNonce>/<userId>/change-password', methods=['PUT'])
def change_password(userNonce,userId):


    request_data = request.get_json()
    change_password = {

        "password": request_data["password"],
        "new_password": request_data["new_password"],
        
        }
    response = requests.put('http://ec2-3-95-53-126.compute-1.amazonaws.com:3700/profile/changePassword/' +userNonce+" / "+userId, data = change_password )
    return response.json()








@retry()
@retry( tries=2, delay=30)
@app.route('/<userNonce>/<userId>/upload-team-document', methods=['POST'])
def upload_team_document(userNonce, userId):


    """
    Used to upload team info to the server
    
    Parameters
    ----------
    userNonce:str
        security dynamic parameter, akin to OTP. Used in conjuction with userId to authenticate requests
    userId
        security dynamic parameter, akin to OTP. Used in conjuction with userNonce to authenticate requests

    Returns
    -------
    str
        Flask response


    
    Sample request: { "team_form" : { "Team Name" : "Spurs",
                    "Founded" : "1890",
                    "Manager" : "Mourinho",
                    "Grounds":"WHL" ,
                    "Location" : "England"  } }

   
    """


    request_data = request.form
    team_data = {
        "upload_json": request_data["document"],
        "location": "documents",
        "category": "team_documents",
        "about": request_data["about"] # Team, name; filled through API client 
    }   
    print(team_data)
    resp = requests.post("http://ec2-3-95-53-126.compute-1.amazonaws.com:3700/utils/upload/A/"+userNonce+"/"+userId, data = team_data)
    return resp.json()


@retry((ConnectionError), tries=2, delay=30)
@app.route('/<userNonce>/<userId>/upload-player-document', methods=['POST'])
def upload_player_document(userNonce, userId):

    """

    
    Used to upload player info to the server. Symbolic link parsing is achieved by following the specified 
    syntax in the PS documentation, a sample request is shown below. 
    
    Parameters
    ----------
    userNonce:str
        security dynamic parameter, akin to OTP. Used in conjuction with userId to authenticate requests
    userId
        security dynamic parameter, akin to OTP. Used in conjuction with userNonce to authenticate requests

    Returns
    -------
    str
        Flask response

    
    Sample Request: 
    
        { "player_form" : { 
                    
                    "Player Name" : "Firminho",
                    "Team":"documents::team_documents::Spurs::Team Name",
                    "Manager":"documents::team_documents::Spurs::Manager",
                    "Country of Residence":"documents::team_documents::Spurs::Location" 
                    
                    }
                    
        }
    
    """
    request_data = request.form
    player_data = {
        
        "upload_json": request_data["document"],   
        

        "location": "documents",
        "category": "player_documents",
        "about": request_data["about"] #In this case, the about is the team name for symbolic search purposes; specified on API form 
        }   
    response = requests.post("http://ec2-3-95-53-126.compute-1.amazonaws.com:3700/utils/upload/A/"+userNonce+"/"+userId, data = player_data)
    return response.json()


@retry((ConnectionError), tries=2, delay=30)
@app.route('/<userNonce>/<userId>/delete-document', methods=['POST'])
def delete_document(userNonce, userId):
    
    
    
    """
    Deletes documents for a certain user, documents to be deleted are specified in the API Client.
    
     Parameters
    ----------
    userNonce:str
        security dynamic parameter, akin to OTP. Used in conjuction with userId to authenticate requests
    userId
        security dynamic parameter, akin to OTP. Used in conjuction with userNonce to authenticate requests

    Returns
    -------
    str
        Flask response


    Sample Request : 
    
    { 
	  "location" : "documents", "category" : "player_documents",
	  "about" :"Spurs" 
    }


    """






    request_data = request.get_json()
    search_params = {
        "search_params": {
            "location": request_data["location"],
            "category": request_data["category"],
            "about": request_data["about"]
        }
    }
    response = requests.post("http://ec2-3-95-53-126.compute-1.amazonaws.com:3700/utils/delete/A/"+userNonce+"/"+userId, json=search_params)
    
    return response.json()


@retry((ConnectionError), tries=2, delay=30)
@app.route('/<userNonce>/<userId>/search-document', methods=['POST'])
def search_document(userNonce, userId):

    """
   
    Utilizes symbolic link parsing for searching documents. Search parameters are imputed over the API Client.
    
     Parameters
    ----------
    userNonce:str
        security dynamic parameter, akin to OTP. Used in conjuction with userId to authenticate requests
    userId
        security dynamic parameter, akin to OTP. Used in conjuction with userNonce to authenticate requests

    Returns
    -------
    str
        Flask response


    Sample Request : 
    
    { 
	  "location" : "documents", "category" : "player_documents",
	  "about" :"Spurs" 
    }


    """

    request_data = request.get_json()
    search_params = {
        "search_params": {
            "location": request_data["location"],
            "category": request_data["category"],
            "about": request_data["about"]
        }
    }
    response = requests.post("http://ec2-3-95-53-126.compute-1.amazonaws.com:3700/utils/download/A/"+userNonce+"/"+userId, json=search_params)
    
    return response.json()

