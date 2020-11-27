"""Handles JSON encoding/decoding"""
import json

def json_decode(encoded_data):
    """Takes encoded data and converts to dictionary"""
    json_string = encoded_data.decode()
    data_dict = json.loads(json_string)
    return data_dict

def json_encode(data_dict):
    """Takes dictionary and converts to encoded data"""
    json_string = json.dumps(data_dict)
    encoded_data = json_string.encode()
    return encoded_data

def generate_keys():
    """
    Generates a public/private key pair
    Returns them in a tuple
    """
    placeholder_keys = ("Public_Key","Private_Key")
    return placeholder_keys