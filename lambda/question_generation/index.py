import os
import json
import boto3
import pydantic
import re
from pydantic import Field
from pydantic import BaseModel
from retrying import retry

from langchain_aws import ChatBedrock

from botocore.config import Config
from botocore.exceptions import ClientError

class BedrockRetryableError(Exception):
    """Class to identify a Bedrock throttling error"""

    def __init__(self, msg):
        super().__init__(self)

        self.message = msg
        
class Question(BaseModel):
    """Details about the question extracted from the text"""
    topic: str = Field(description="The topic of the question")
    subtopic: str = Field(description="The subtopic of the question")
    questionText: str = Field(description="The actual question text")
    options: list = Field(description="Array of answer options")
    correctOptions: list = Field(description="Array of optionIds that are correct")
    difficulty: int = Field(description="Difficulty level of the question")
    tags: list = Field(description="Array of tags for the question")

CLAUDE_INFORMATION_EXTRACTION_SYSTEM_PROMPT_EN = """You are an advanced information extraction system. Your job is to extract key information from the text presented to you and put it in JSON format. The information you generate will be consumed by other systems which is why its highly importat that you place the information in a JSON object. You work with sensitive, very important information which is why you are extremely cautious when extracting the information reasoning thoroughly about the extracted information.

You always behave in a professional, reliable, and confident manner.

For this task you are the follow this rules:

- NEVER ignore any of this rules otherwise the user will be very upset
- Before you start extracting the information you will first think about the information you have available and the information you need to extract and place your reasoning in <thinking>
- Before you start extracting the information you will first determine how confident you are that you can extract the requested information with a number between 0 and 100. Place this number in the field <confidence_level>.
- NEVER extract information from which you are not confident, as a minimum you need 70 points of confidence to extract the requested information
- Place your conclusion in <conclusion> about whether you can or cannot extract the requested information
- It is okay if you cannot extract the requested information, the information is very sensitive and you only extract information of which you are confident
- ALWAYS extract the information in a JSON object, otherwise your work has no purpose
- Place the information you extract in <extracted_information>
- Do not fill all the values, only extract the values from which you are completely confident
- When you are not confident about a value leave the field empty
- If you cannot extract the requested information, generate a JSON object with empty values

Your confident level is calculated according to the following criteria:

- confidence_level<0 if the requested information is not contained in the original text
- 20<confidence_level<60 if part of the requested information is contained in the original text
- 60<confidence_level<90 if the requested information can be inferred from information in the original text
- 90<confidence_level if all the requested information is contained in the original text

Your answer must always contain the following elements:

- <thinking>: Your reasoning about the information you have available and the information you need to extract
- <confidence_level>: The confidence level you have in extracting the requested information
- <conclusion>: Your conclusion about whether you can or cannot extract the requested information
- <extracted_information>: The information you extract in a JSON object

This is the JSON schema you must follow to extract the information:

<json_schema>
{json_schema}
</json_schema>
"""

class InformationExtraction(BaseModel):
    """Details about the information extraction task the LLM performed"""
    thinking: str = Field(description="The reasoning of the LLM about the information to extract and the presented text")
    confidence_level: int = Field(0, description="The level of confidence the LLM shows about extracting the requested information")
    conclusion: bool = Field(False, description="Whether the LLM considers the requested information can be extracted from the presented text")
    extracted_information: str = Field(description="The information extracted by the LLM")

BEDROCK_REGION = os.environ.get("BEDROCK_REGION")
SOURCE_DOCUMENTS_BUCKET = os.environ.get("SOURCE_DOCUMENTS_BUCKET")
QUESTIONS_TABLE = os.environ.get("QUESTIONS_TABLE")
BEDROCK_MODEL_ID = os.environ.get("BEDROCK_MODEL_ID")

INFORMATION_EXTRACTION_MODEL_PARAMETERS = {
    "max_tokens": 1500,
    "temperature": 0.1,
    "top_k": 20,
}

FORMAT_RESPONSES_CLAUDE_PARAMETERS = {
    "max_tokens": 1500,
    "temperature": 0,
    "top_k": 20,
}

bedrock_runtime = boto3.client(
    service_name="bedrock-runtime",
    region_name=BEDROCK_REGION,
    config=Config(retries={'max_attempts': 20})
)

table = boto3.resource("dynamodb").Table(QUESTIONS_TABLE)

@retry(wait_exponential_multiplier=10000, wait_exponential_max=60000, stop_max_attempt_number=10,
       retry_on_exception=lambda ex: isinstance(ex, BedrockRetryableError))
def text_information_extraction(text: str) -> BaseModel:

    bedrock_llm = ChatBedrock(
        model_id=BEDROCK_MODEL_ID,
        model_kwargs=INFORMATION_EXTRACTION_MODEL_PARAMETERS,
        client=bedrock_runtime,
    )
    
    claude_information_extraction_prompt_template = CLAUDE_INFORMATION_EXTRACTION_SYSTEM_PROMPT_EN

    structured_llm = bedrock_llm.with_structured_output(Question)

    structured_chain = claude_information_extraction_prompt_template | structured_llm

    # Retry mechanism to workaround Bedrock Throttling
    try:
        print(f"Extracting information")
        information_extraction_obj = structured_chain.invoke({
            "json_schema": Question.model_json_schema(),
            "text": text
        })
    except ClientError as exc:
        if exc.response['Error']['Code'] == 'ThrottlingException':
            print("Bedrock throttling. To try again")
            raise BedrockRetryableError(str(exc))
        elif exc.response['Error']['Code'] == 'ModelTimeoutException':
            print("Bedrock ModelTimeoutException. To try again")
            raise BedrockRetryableError(str(exc))
        else:
            raise
    except bedrock_runtime.exceptions.ThrottlingException as throttlingExc:
        print("Bedrock ThrottlingException. To try again")
        raise BedrockRetryableError(str(throttlingExc))
    except bedrock_runtime.exceptions.ModelTimeoutException as timeoutExc:
        print("Bedrock ModelTimeoutException. To try again")
        raise BedrockRetryableError(str(timeoutExc))
    except Exception as e:

        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(e).__name__, e.args)
        print(message)
        raise

    return information_extraction_obj

def lambda_handler(event, context):
    """
    Lambda function to generate questions from a text document
    @param event:
    @param context:
    @return:
    """
    
    print("Received event: ", event)
    
    doc_text = event["text"]
    chunk_index = event["chunk_index"]
    
    extracted_information = {}
    
    try:
        # Invoke the model to extract the information
        print(f"Extracting information")
        question = text_information_extraction(doc_text)
        print(f"Extracted question: {question}")
        

    except pydantic.ValidationError as e:
        print(f"Pydantic Validation error: {e}")
    except Exception as e:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(e).__name__, e.args)
        print(message)
        raise

    print(f"Extracted information: {extracted_information}")

    return {
        "statusCode": 200,
        "body": {
            "extracted_information": extracted_information,
            "chunk_index": chunk_index
        }
    }