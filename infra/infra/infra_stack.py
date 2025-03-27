from aws_cdk import (
    # Duration,
    Stack,
    CfnOutput,
    # aws_sqs as sqs,
)
from constructs import Construct
from .constructs.backend import BackendConstruct

class InfraStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create the backend construct
        backend = BackendConstruct(self, "Backend")

        # Add outputs
        CfnOutput(
            self, "SourceDocumentsBucketName",
            value=backend.sourceDocumentsBucket.bucket_name,
            description="Name of the source documents S3 bucket"
        )

        CfnOutput(
            self, "DocumentProcessingLambdaFunctionName",
            value=backend.documentProcessingLambda.function_name,
            description="Name of the document processing Lambda function"
        )

        CfnOutput(
            self, "QuestionGenerationLambdaFunctionName",
            value=backend.questionGenerationLambda.function_name,
            description="Name of the question generation Lambda function"
        )

        CfnOutput(
            self, "QuestionStoringLambdaFunctionName",
            value=backend.questionStoringLambda.function_name,
            description="Name of the question storing Lambda function"
        )

        CfnOutput(
            self, "QuestionsTableName",
            value=backend.questionsTable.table_name,
            description="Name of the questions table"
        )

        # The code that defines your stack goes here

        # example resource
        # queue = sqs.Queue(
        #     self, "InfraQueue",
        #     visibility_timeout=Duration.seconds(300),
        # )
