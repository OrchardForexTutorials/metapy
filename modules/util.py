import argparse
import json
import os
from types import SimpleNamespace
import datetime

def load_config_from_args():

    # Initialize the parser
    parser = argparse.ArgumentParser(description="Python - Metatrader trading robot")

    # first argument is the path to configuration
    parser.add_argument("config_path", nargs="?", type=str, help="Path to the configuration file")

    # Add named optional arguments
    parser.add_argument("--testing", type=bool, help="Run in test mode")
    parser.add_argument("--mt_path", type=str, help="Path to Metatrader exe")
    parser.add_argument("--cycle", type=int, help="Cycle time")

    # Parse the arguments
    args = parser.parse_args()

    config_path = args.config_path if args.config_path else 'configuration/config.json'

    config = load_config(config_path)
    if config is None:
        log(f'Invalid configuration file {config_path}')
        quit()

    for attr in ["testing", "mt_path", "cycle"]:
        value = getattr(args, attr, None)
        if value:
            setattr(config, attr, value)

    return config

def load_config(path):

    base_path = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_path, '..', path)
    
    try:

        with open(config_path, "r") as file:
            content = file.read()

    except FileNotFoundError:
        print(f"Error config file {path} not found")
        return None

    try:

        # Parse string into a dot-notation object
        return json.loads(content, object_hook=lambda d: SimpleNamespace(**d))

    except json.JSONDecodeError:
        print("config file is not valid json format")
        return None

def log(msg):

    now = datetime.datetime.now()
    now_str = now.strftime('%Y.%m.%d %H:%M:%S')
    msg = f"{now_str} {msg}"
    print(msg)
