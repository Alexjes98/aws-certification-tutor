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
from aws_cdk.aws_lambda import DockerImageFunction, DockerImageCode, Function


class BackendConstruct(Construct):
    sourceDocumentsBucket: s3.Bucket
    documentProcessingLambda: DockerImageFunction
    questionGenerationLambda: DockerImageFunction
    questionStoringLambda: Function
    questionsTable: dynamodb.Table

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create S3 bucket
        self.sourceDocumentsBucket = s3.Bucket(
            self, "SourceDocumentsBucket",
            encryption=s3.BucketEncryption.S3_MANAGED,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )
        
        self.questionsTable = dynamodb.Table(
            self, "QuestionsTable",
            partition_key=dynamodb.Attribute(name="question_id", type=dynamodb.AttributeType.STRING),
            removal_policy=RemovalPolicy.DESTROY,
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

        self.sourceDocumentsBucket.grant_read(self.documentProcessingLambda)

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

        # Add Bedrock policy to question generation lambda
        bedrock_policy = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["bedrock:InvokeModel"],
            resources=["*"]
        )
        self.questionGenerationLambda.add_to_role_policy(bedrock_policy)
        
        # Create question storing lambda
        self.questionStoringLambda = Function(
            self, "QuestionStoringLambda",
            code=lambda_.Code.from_asset(".././lambda/question_storing"),
            handler="index.lambda_handler",
            runtime=lambda_.Runtime.PYTHON_3_10,
            environment={
                "QUESTIONS_TABLE_NAME": self.questionsTable.table_name
            }
        )

        self.questionsTable.grant_read_write_data(self.questionStoringLambda)