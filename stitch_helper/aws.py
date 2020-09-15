#!/usr/bin/env python3

import boto3
import json
import os
import time

LAYER_CACHE_TIME = 60 * 60 * 1
LAYER_CACHE_FILE = os.path.expanduser("~/.stitch_aws_layer_cache")

def recent_file(fname, cache_time):
    return os.path.exists(fname) and (time.time() - os.stat(fname).st_mtime) < cache_time

def get_stacks():
    return boto3.client("opsworks").describe_stacks()["Stacks"]

def get_stack_layers(stack_id):
    return boto3.client("opsworks").describe_layers(StackId=stack_id)["Layers"]

def get_all_layers():
    if recent_file(LAYER_CACHE_FILE, LAYER_CACHE_TIME):
        with open(LAYER_CACHE_FILE) as f:
            return json.load(f)

    all_layers = {}
    for stack in get_stacks():
        layers = get_stack_layers(stack["StackId"])
        for layer in layers:
            layer["StackName"] = stack["Name"]
            all_layers[layer["Name"]] = layer

    with open(LAYER_CACHE_FILE, "w") as f:
        json.dump(all_layers, f)

    return all_layers

def get_layer_instances(layer_id):
    return [
        instance
        for instance in boto3.client("opsworks").describe_instances(LayerId=layer_id)["Instances"]
        if "PrivateIp" in instance
    ]
