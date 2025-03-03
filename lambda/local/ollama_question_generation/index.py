from langchain_ollama.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts.chat import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate, \
    AIMessagePromptTemplate
from pydantic import BaseModel, Field

import pymupdf
from typing import List, Optional

# Define the structured output model

class Option(BaseModel):
    """Answer option"""
    optionId: str = Field(description="The optionId")
    optionText: str = Field(description="The text of the option")
    explanation: str = Field(
        description="Explanation of the correctness of the option")


class Question(BaseModel):
    """Question extracted from the text"""
    topic: str = Field(description="The topic of the question")
    # subtopic: str = Field(description="The subtopic of the question")
    questionText: str = Field(description="The actual question text")
    options: List[Option] = Field([], description="Array of answer options")
    correctOptions: List[str] = Field(
        [], description="Array of optionIds that are correct")
    # difficulty: int = Field(description="Difficulty level of the question")
    # tags: List[str] = Field(description="Array of tags for the question")


class Result(BaseModel):
    """Details about the result extracted from the text"""
    thinking: str = Field(
        description="Your reasoning about the information you have available and the information you need to extract")
    conclusion: str = Field(
        description="Your conclusion about whether you can or cannot extract the requested information")
    confidence_level: int = Field(
        description="The confidence level you have in extracting the requested information")
    formulated_question: str = Field(description="The formulated question")


# TODO: VALIDATE SCHEMA TO AVOID PARSER ERRORS
# TODO: AVOID QUESTIONS FOR VERY SPECIFIC EXAMPLES IN THE DOCUMENTATION (E.G., EXAMPLES, CODE SNIPPETS)
# TODO: AVOID QUESTIONS FOR VERY SPECIFIC INFORMATION (E.G., STEPS TO DELETE A RESOURCE)
# TODO: AVOID QUESTIONS ABOUT THE DOCUMENTATION ITSELF (E.G., "WHAT IS THE NAME OF THE DOCUMENT?")

# CHECK USING DEEPTHINK MODELS TO AVOID ADDING THOUGHTS TO THE QUESTION
# - Before you start generating the question you will first think about the information you have available and the information you need to extract and place your reasoning in <thinking>
# - <thinking>: Your reasoning about the information you have available and the information you need to generate the question
CLAUDE_QUESTION_GEN_SYSTEM_PROMPT_EN = """You are an advanced question generation system.
Your job is to generate questions with key information from the text presented to you and put it in JSON format.
The information you generate will be consumed by other systems which is why its highly importat that you place the information in a JSON object. You work with sensitive, very important information which is why you are extremely cautious when extracting the information reasoning thoroughly about the extracted information.

You always behave in a professional, reliable, and confident manner.

For this task you are the follow this rules:

- NEVER ignore any of this rules otherwise the user will be very upset

- Before you start generating the question the information you will first determine how confident you are that you can generate the question with a number between 0 and 100. Place this number in the field <confidence_level>.
- NEVER generate questions from which you are not confident, as a minimum you need 70 points of confidence to extract the requested information
- Place your conclusion in <conclusion> about whether you can or cannot generate the question
- It is okay if you cannot generate the question, the information is very sensitive and you only extract information of which you are confident
- ALWAYS generate the questions in a JSON object, otherwise your work has no purpose
- Place the question you generate in <generated_question>
- When you are not confident about a value leave the field empty
- If you cannot generate the question, generate a JSON object with empty values

Your confident level is calculated according to the following criteria:

- confidence_level<0 if any AWS Certification information is not contained in the original text
- 20<confidence_level<60 if part of the AWS Certification information is contained in the original text but contains irrelevant examples
- 60<confidence_level<90 if the AWS Certification information can be inferred from information in the original text
- 90<confidence_level if all the AWS Certification information is contained in the original text

Your answer must always contain the following elements:


- <confidence_level>: The confidence level you have in generating the question
- <conclusion>: Your conclusion about whether you can or cannot generate the question
- <generated_question>: The question you generate in a JSON object

This is the JSON schema you must follow to generate the question:

<json_schema>
{json_schema}
</json_schema>
"""

CLAUDE_QUESTION_GEN_USER_PROMPT_EN = """
Extract the information from the following text:

<text>
{text}
</text>
"""

# Create the prompt template with instructions for structured extraction


def test():
    # Create the Ollama chat model (using DeepSeek)
    chat_model = ChatOllama(
        model="llama3.2", 
        temperature=0.0
    )

    structured_llm = chat_model.with_structured_output(Question)

    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(CLAUDE_QUESTION_GEN_SYSTEM_PROMPT_EN, input_variables=[
                                                  "json_schema"], validate_template=True),
        HumanMessagePromptTemplate.from_template(
            CLAUDE_QUESTION_GEN_USER_PROMPT_EN, input_variables=["text"], validate_template=True),
    ])

    structured_chain = prompt | structured_llm

    # open a document
    doc = pymupdf.open("../../sample_files/AWSLambda-DeveloperGuide.pdf")
    # TODO: CLEAN UP THE TEXT BEFORE SENDING TO THE MODEL TO AVOID IRRELEVANT QUESTIONS

    results_per_page = []

    for page in doc:  # iterate the document pages
        try:
            text = page.get_text().encode("utf8")  # get plain text (is in UTF-8)
            # Invoke the chain
            question_object = structured_chain.invoke({
                "json_schema": Question.model_json_schema(),
                "text": text})
            print(question_object)
            break
        except Exception as e:
            print(e)
            break

    for result in results_per_page:
        print(result)


if __name__ == "__main__":
    test()
