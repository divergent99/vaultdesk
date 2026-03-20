import os
from dotenv import load_dotenv

load_dotenv()
AUTH0_DOMAIN    = os.environ["AUTH0_DOMAIN"]
CLIENT_ID       = os.environ["AUTH0_CLIENT_ID"]
CLIENT_SECRET   = os.environ["AUTH0_CLIENT_SECRET"]
SECRET_KEY      = os.environ["SECRET_KEY"]

AWS_REGION      = os.environ.get("AWS_REGION", "us-east-1")
AWS_ACCESS_KEY  = os.environ["AWS_ACCESS_KEY_ID"]
AWS_SECRET_KEY  = os.environ["AWS_SECRET_ACCESS_KEY"]

PORT = int(os.environ.get("PORT", 8001))
