import os
from dotenv import dotenv_values

def load_env():
    env_vars = dotenv_values(".env")
    for key, value in env_vars.items():
        os.environ[key] = value

if __name__ == "__main__":
    load_env()
    print("Environment variables loaded into this session.")
