import os
from dotenv import load_dotenv
from strands.models.bedrock import BedrockModel

load_dotenv()

bedrock_model = BedrockModel(
    model_id="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
    region_name='us-west-2',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    temperature=0.3,
) 