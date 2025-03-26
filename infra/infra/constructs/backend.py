import os
from constructs import Construct
from aws_cdk import (
    RemovalPolicy,
    Duration,
    aws_dynamodb as dynamodb,
    aws_s3 as s3,
    aws_sqs as sqs,
    aws_lambda as lambda_,
    aws_iam as iam,
)
from aws_cdk.aws_lambda import DockerImageFunction, DockerImageCode


class BackendConstruct(Construct):
    sourceDocumentsBucket: s3.Bucket
    documentProcessingLambda: DockerImageFunction
    questionGenerationLambda: DockerImageFunction

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create S3 bucket
        self.sourceDocumentsBucket = s3.Bucket(
            self, "SourceDocumentsBucket",
            encryption=s3.BucketEncryption.S3_MANAGED,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )

        # Create document processing lambda
        self.documentProcessingLambda = DockerImageFunction(
            self, "DocumentProcessingLambda",
            code=DockerImageCode.from_image_asset(".././lambda/pdf_extraction",
                                                  cmd=["index.lambda_handler"],
                                                  file="Dockerfile"),
            architecture=lambda_.Architecture.X86_64,
            memory_size=512,
            timeout=Duration.minutes(5),
        )
        
        #"An error occurred (AccessDeniedException) when calling the Converse operation: User: arn:aws:sts::231149472867:assumed-role/CertificationTutorStack-BackendQuestionGenerationLa-NYPJhwvg1LaA/CertificationTutorStack-BackendQuestionGenerationL-M8KCFiXwE7f8 is not authorized to perform: bedrock:InvokeModel on resource: arn:aws:bedrock:us-east-1::foundation-model/amazon.nova-lite-v1:0 because no identity-based policy allows the bedrock:InvokeModel action"
        #TODO: Add bedrock policy to lambda to allow access to bedrock

        # Create question generation lambda
        self.questionGenerationLambda = DockerImageFunction(
            self, "QuestionGenerationLambda",
            code=DockerImageCode.from_image_asset(".././lambda/question_generation",
                                                  cmd=["index.lambda_handler"],
                                                  file="Dockerfile"),
            architecture=lambda_.Architecture.X86_64,
            memory_size=512,
            timeout=Duration.minutes(5),
            environment={
                "BEDROCK_REGION": os.environ.get("BEDROCK_REGION"),
                "QUALITY_THRESHOLD": os.environ.get("QUALITY_THRESHOLD"),
                "BEDROCK_MODEL_ID": os.environ.get("BEDROCK_MODEL_ID"),
            }
        )
