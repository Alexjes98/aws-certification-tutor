import os
import boto3
import pydantic
from pydantic import Field
from pydantic import BaseModel
from retrying import retry

from langchain_aws import ChatBedrock

from botocore.config import Config
from botocore.exceptions import ClientError
from langchain_core.prompts.chat import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate

BEDROCK_REGION = os.environ.get("BEDROCK_REGION")
BEDROCK_MODEL_ID = os.environ.get("BEDROCK_MODEL_ID")
QUALITY_THRESHOLD = float(os.environ.get("QUALITY_THRESHOLD", "0.7"))

class BedrockRetryableError(Exception):
    """Class to identify a Bedrock throttling error"""

    def __init__(self, msg):
        super().__init__(self)

        self.message = msg
class Question(BaseModel):
    """Details about the question extracted from the text"""
    questionText: str = Field(description="The actual question text", alias="question_text")
    options: list = Field(description="Array of answer options")
    correctOptions: list = Field(
        description="Array of optionIds that are correct", alias="correct_options")
    tags: list = Field(
        description="Array of tags of question topics", default=[])
    quality_score: float = Field(
        description="A score from 0-1 indicating the quality of the question", default=0.0)

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True

QUESTION_GENERATION_PROMPT = """You are an advanced question generation system specialized in creating AWS certification questions.
Your job is to generate high-quality multiple-choice questions based on the text provided.

GUIDELINES:
- Create questions that test understanding of AWS concepts, services, and best practices
- Focus on practical knowledge that would be tested in AWS certification exams
- Generate clear, unambiguous questions with 4-5 answer options
- Ensure at least one option is correct (sometimes multiple may be correct)
- Avoid questions about documentation specifics, code examples, or irrelevant details
- If the text doesn't contain sufficient AWS-related information, return an empty question

OUTPUT FORMAT:
Generate a structured question with the following fields:
- questionText: The actual question being asked
- options: Array of possible answers (4-5 options)
- correctOptions: Array of indices of correct answers (0-based)
- tags: Array of tags of question topics
- quality_score: Your assessment (0.0-1.0) of how well the question tests AWS certification knowledge

IMPORTANT: Your response must be a valid JSON object matching the schema provided. Do not include any explanations or text outside of the JSON structure.
This is the JSON schema you must follow:

<json_schema>
{json_schema}
</json_schema>
"""

INFORMATION_EXTRACTION_USER_PROMPT_EN = """
Extract the information from the following text:

<text>
{text}
</text>
"""

QUESTION_GENERATION_MODEL_PARAMETERS = {
    "max_tokens": 1500,
    "temperature": 0.2,  # Slightly higher temperature for more creative questions
    "top_k": 250,
    "top_p": 0.9,
}

bedrock_runtime = boto3.client(
    service_name="bedrock-runtime",
    region_name=BEDROCK_REGION,
    config=Config(retries={'max_attempts': 20})
)

@retry(wait_exponential_multiplier=10000, wait_exponential_max=60000, stop_max_attempt_number=10,
       retry_on_exception=lambda ex: isinstance(ex, BedrockRetryableError))
def generate_question(text: str) -> Question:
    """
    Generate a question from the provided text using Bedrock LLM

    @param text: The text to generate a question from
    @return: A Question object
    @raise: BedrockRetryableError if the Bedrock API returns a throttling error
    @raise: Exception if an error occurs during the question generation process
    """

    bedrock_llm = ChatBedrock(
        model_id=BEDROCK_MODEL_ID,
        model_kwargs=QUESTION_GENERATION_MODEL_PARAMETERS,
        client=bedrock_runtime,
    )

    # Create a proper chat prompt template combining both prompts
    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(QUESTION_GENERATION_PROMPT),
        HumanMessagePromptTemplate.from_template(
            INFORMATION_EXTRACTION_USER_PROMPT_EN)
    ])

    # Use structured output directly
    structured_llm = bedrock_llm.with_structured_output(Question)

    # Create the chain with the combined prompt
    structured_chain = prompt | structured_llm

    # Retry mechanism to workaround Bedrock Throttling
    try:
        print(f"Generating question from text")
        raw_output = structured_chain.invoke({
            "json_schema": Question.model_json_schema(),
            "text": text
        })
        print(f"Raw LLM output: {raw_output}")
        question = raw_output
        return question
    except ClientError as exc:
        if exc.response['Error']['Code'] in ['ThrottlingException', 'ModelTimeoutException']:
            print(f"Bedrock {exc.response['Error']['Code']}. Retrying...")
            raise BedrockRetryableError(str(exc))
        else:
            raise
    except (bedrock_runtime.exceptions.ThrottlingException,
            bedrock_runtime.exceptions.ModelTimeoutException) as e:
        print(f"Bedrock exception: {type(e).__name__}. Retrying...")
        raise BedrockRetryableError(str(e))
    except Exception as e:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(e).__name__, e.args)
        print(message)
        raise


def is_valid_question(question: Question) -> bool:
    """Validate if the generated question meets quality criteria"""
    # Check if question has sufficient quality score
    if question.quality_score < QUALITY_THRESHOLD:
        return False

    # Check if question has valid content
    if not question.questionText or not question.options or not question.correctOptions:
        return False

    # Check if correctOptions references valid options
    if any(idx >= len(question.options) for idx in question.correctOptions):
        return False

    return True


def lambda_handler(event, context):
    """
    Lambda function to generate questions from a text document
    @param event:
    @param context:
    @return:
    """
    
    print(f"Received event: {event}")

    page_text = event["page_text"]
    page_index = event["page_index"]

    try:
        # Generate question from the text
        question = generate_question(page_text)
        print(f"Generated question: {question}")

        # Validate the question
        question_valid = is_valid_question(question)

        return {
            "statusCode": 200,
            "body": {
                "question": question.model_dump() if question_valid else None,
                "is_valid": question_valid,
                "page_index": page_index
            }
        }
    except pydantic.ValidationError as e:
        print(f"Pydantic Validation error: {e}")
        return {
            "statusCode": 400,
            "body": {
                "error": str(e)
            }
        }
    except Exception as e:
        print(f"An error occurred: {e}")
        return {
            "statusCode": 500,
            "body": {
                "error": str(e)
            }
        }