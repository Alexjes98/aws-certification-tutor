import os
from constructs import Construct
from aws_cdk import (
    CfnOutput,
    RemovalPolicy,
    aws_s3 as s3,
    aws_s3_deployment as s3_deployment,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as cloudfront_origins,
    aws_dynamodb as dynamodb,
    aws_cognito as cognito,
)


class StorageConstruct(Construct):
    sourceDocumentsBucket: s3.Bucket
    questionsTable: dynamodb.Table
    frontendBucket: s3.Bucket

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # Questions table
        self.questionsTable = dynamodb.Table(
            self, "QuestionsTable",
            partition_key=dynamodb.Attribute(
                name="question_id", type=dynamodb.AttributeType.STRING),
            removal_policy=RemovalPolicy.DESTROY,
        )
        # Document source bucket
        self.sourceDocumentsBucket = s3.Bucket(
            self, "SourceDocumentsBucket",
            encryption=s3.BucketEncryption.S3_MANAGED,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )
        # Create S3 bucket for static web app
        self.frontendBucket = s3.Bucket(
            self, "FrontendBucket",
            versioned=True,
            encryption=s3.BucketEncryption.S3_MANAGED,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )

        CfnOutput(
            self, "SourceDocumentsBucketName",
            value=self.sourceDocumentsBucket.bucket_name,
            description="Name of the source documents bucket"
        )

        CfnOutput(
            self, "QuestionsTableName",
            value=self.questionsTable.table_name,
            description="Name of the questions table"
        )

        CfnOutput(
            self, "FrontendBucketName",
            value=self.frontendBucket.bucket_name,
            description="Name of the frontend bucket"
        )
