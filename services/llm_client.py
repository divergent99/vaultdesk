import boto3
from langchain_aws import ChatBedrockConverse
from config.settings import AWS_REGION, AWS_ACCESS_KEY, AWS_SECRET_KEY

bedrock_client = boto3.client(
    "bedrock-runtime",
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
)

llm = ChatBedrockConverse(
    client=bedrock_client,
    model="us.amazon.nova-lite-v1:0",
    max_tokens=2048,
    temperature=0,
)
