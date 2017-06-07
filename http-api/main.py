#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import argparse
import json
import urllib.request as urllib
import time

from http.server import HTTPServer
from vk_auth import VKAuth
from webbrowser import open_new
from urllib.parse import urlencode

APP_ID = "6036474"


def call_api(method, params, token):
    params.append(("access_token", token))
    url = "https://api.vk.com/method/{}?{}".format(method, urlencode(params))
    res = urllib.urlopen(url).read().decode('utf-8')
    json_result = json.loads(str(res))
    if "response" not in json_result:
        return ""
    return json_result["response"]


def get_user_id(token):
    return call_api("users.get", [], token)[0]["uid"]


def get_user_name(token, user_id):
    answer = call_api("users.get", [("user_ids", user_id)], token)[0]
    return "{} {}".format(answer["first_name"], answer["last_name"])


def get_friends(user_id, token):
    return call_api("friends.get", [("uid", user_id)], token)


def get_group_ids(user_id, token):
    group_ids = call_api("groups.get", [("uid", user_id)], token)
    return group_ids
    

def get_access_token():
    authorization_request = construct_authorization_request()
    open_new(authorization_request)
    address = ('localhost', 31337)
    http_server = HTTPServer(address, VKAuth)
    http_server.socket.settimeout(25)
    http_server.handle_request()
    return VKAuth.access_token


def construct_authorization_request():
    params = [
        ("client_id", APP_ID),
        ("display", "page"),
        ("v", "5.64"),
        ("redirect_uri", "http://localhost:31337/"),
        ("response_type", "code"),
        ("scope", "friends,groups")        
    ]
    return 'https://oauth.vk.com/authorize?' + urlencode(params)

    
def print_progress(current, maximum):
    percentage = int((current / maximum) * 10)
    print("\r" + percentage * "#" + (10 - percentage) * ".", end="")


def get_top_by_groups(user_id, token, friends):
    my_group_ids = set(get_group_ids(user_id, token))
    friends_with_groups = []
    number_of_friends = len(friends)
    
    print("Получаю информацию о группах")
    for num, friend_id in enumerate(friends):
        time.sleep(0.4)
        print_progress(num, number_of_friends)
        friend_group_ids = set(get_group_ids(friend_id, token))
        common_groups = friend_group_ids.intersection(my_group_ids)
        friends_with_groups.append([len(common_groups), friend_id])
    print()
    
    friends_with_groups.sort(reverse=True)
    print("Получаю информацию о именах друзей")
    for num, (_, friend_id) in enumerate(friends_with_groups):
        time.sleep(0.4)
        print_progress(num, number_of_friends)
        friends_with_groups[num][1] = get_user_name(token, friend_id)
    print()
    return friends_with_groups

def parse_args():
    """Create argument parser"""
    p = argparse.ArgumentParser(description="Get top of your friends sorted by common groups!")
    return p.parse_args()

    
def main():
    parse_args()
    token = get_access_token()
    user_id = get_user_id(token)

    friends = get_friends(user_id, token)    
    friends_with_groups = get_top_by_groups(user_id, token, friends)
    
    print("Топ друзей")
    for (friend_groups, friend_name) in friends_with_groups:
        print(friend_name, friend_groups)
    
    
if __name__ == '__main__':
    main()
