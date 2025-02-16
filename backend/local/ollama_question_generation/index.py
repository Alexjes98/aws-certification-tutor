from langchain_ollama.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
import pymupdf
from typing import List, Optional

# Define the structured output model

class Question(BaseModel):
    """Details about the question extracted from the text"""
    topic: str = Field(description="The topic of the question")
    subtopic: str = Field(description="The subtopic of the question")
    questionText: str = Field(description="The actual question text")
    options: List[dict] = Field([], description="Array of answer options")
    correctOptions: List[str] = Field([],description="Array of optionIds that are correct")
    difficulty: int = Field(description="Difficulty level of the question")
    tags: List[str] = Field(description="Array of tags for the question")

class Result(BaseModel):
    """Details about the result extracted from the text"""
    thinking: Optional[str]  = Field(description="Your reasoning about the information you have available and the information you need to extract")
    conclusion: Optional[str] = Field(description="Your conclusion about whether you can or cannot extract the requested information")
    generated_question: Question = Field(description="The text extracted from the document")


# TODO: VALIDATE SCHEMA TO AVOID PARSER ERRORS
# TODO: AVOID QUESTIONS FOR VERY SPECIFIC EXAMPLES IN THE DOCUMENTATION (E.G., EXAMPLES, CODE SNIPPETS)
# TODO: AVOID QUESTIONS FOR VERY SPECIFIC INFORMATION (E.G., STEPS TO DELETE A RESOURCE)
# TODO: AVOID QUESTIONS ABOUT THE DOCUMENTATION ITSELF (E.G., "WHAT IS THE NAME OF THE DOCUMENT?")
CLAUDE_QUESTION_GEN_SYSTEM_PROMPT_EN = """You are an advanced AWS Certification Questions generation system. Your task is to generate a multiple-choice question based on the text provided. The question should be relevant to the text and test the reader's understanding of the topic. The question should have a clear topic, subtopic, question text, answer options, correct options, difficulty level, and tags. Your question should be challenging but fair, and the answer should be directly inferable from the text.

You always behave in a professional, reliable, and confident manner.

For this task you are the follow this rules:

- NEVER ignore any of this rules otherwise the user will be very upset
- Before you start extracting the information you will first think about the information you have available and the information you need to extract and place your reasoning in <thinking>
- Place your conclusion in <conclusion> about whether you can or cannot extract the requested information
- ALWAYS extract the information in a JSON object, otherwise your work has no purpose
- Place the information you extract in <generated_question>
- For the options field, generate an array of JSON objects with the fields optionId (A,B,C), optionText (the text of the answer option), and explanation (explanation of why this option is correct/incorrect)
- Do not fill all the values, only extract the values from which you are completely confident
- When you are not confident about a value leave the field empty
- If you cannot extract the requested information, generate a JSON object with empty values

Your answer must always contain the following elements:

- <thinking>: Your reasoning about the information you have available and the information you need to extract to generate the question
- <conclusion>: Your conclusion about whether you can or cannot generate the question
- <generated_question>: The information you extract in a JSON object

This is the JSON schema you must follow to extract the information:

<json_schema>
{json_schema}
</json_schema>
"""

# Create the output parser
question_parser = PydanticOutputParser(pydantic_object=Result)
parser = PydanticOutputParser(pydantic_object=Question)

# Create the prompt template with instructions for structured extraction


def test():
    prompt = ChatPromptTemplate.from_messages([
        ("system", CLAUDE_QUESTION_GEN_SYSTEM_PROMPT_EN),
        ("human", "Text to analyze: {text}")
    ])

    # Add format instructions to the prompt
    prompt = prompt.partial(
        format_instructions=parser.get_format_instructions())

    # Create the Ollama chat model (using DeepSeek)
    chat_model = ChatOllama(
        model="deepseek-r1",  # Ensure this model is pulled via `ollama pull deepseek-1`
        temperature=0.0  # Set to 0 for more deterministic output
    )

    # Create the full chain
    chain = prompt | chat_model | question_parser

    # open a document
    doc = pymupdf.open("../../sample_files/AWSLambda-DeveloperGuide.pdf")
    # TODO: CLEAN UP THE TEXT BEFORE SENDING TO THE MODEL TO AVOID IRRELEVANT QUESTIONS
    
    results_per_page = []

    for page in doc:  # iterate the document pages
        try:
            text = page.get_text().encode("utf8")  # get plain text (is in UTF-8)
            # Invoke the chain
            result = chain.invoke(
                {"text": text, "json_schema": Question.model_json_schema()})
            print(result)
            results_per_page.append(result)
        except Exception as e:
            print(e)
        
    for result in results_per_page:
        print(result)


if __name__ == "__main__":
    test()
