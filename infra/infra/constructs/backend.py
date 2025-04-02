import os
from constructs import Construct
from aws_cdk import (
    CfnOutput,
    Duration,
    aws_dynamodb as dynamodb,
    aws_s3 as s3,
    aws_lambda as lambda_,
    aws_iam as iam,
    aws_apigateway as apigateway,
    aws_cognito as cognito,
)
from aws_cdk.aws_lambda import DockerImageFunction, DockerImageCode, Function


class BackendConstruct(Construct):
    documentProcessingLambda: DockerImageFunction
    questionGenerationLambda: DockerImageFunction
    questionStoringLambda: Function
    api_gateway_rest_api: apigateway.RestApi
    documentCrudLambda: lambda_.Function
    questionsCrudLambda: lambda_.Function
    authorizer: apigateway.CognitoUserPoolsAuthorizer

    def __init__(self, scope: Construct, construct_id: str, source_documents_bucket: s3.Bucket, questions_table: dynamodb.Table, user_pool: cognito.UserPool, frontend_url: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

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

        source_documents_bucket.grant_read(self.documentProcessingLambda)

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
                "QUESTIONS_TABLE_NAME": questions_table.table_name
            }
        )

        questions_table.grant_read_write_data(self.questionStoringLambda)

        # Create Document CRUD Lambda
        self.documentCrudLambda = lambda_.Function(
            self, "DocumentCrudLambda",
            code=lambda_.Code.from_asset(".././lambda/document_crud"),
            handler="index.lambda_handler",
            runtime=lambda_.Runtime.PYTHON_3_10,
            environment={
                "SOURCE_BUCKET_NAME": source_documents_bucket.bucket_name
            },
            timeout=Duration.seconds(30)
        )

        # Grant Document CRUD Lambda permissions to interact with S3 bucket
        source_documents_bucket.grant_read_write(self.documentCrudLambda)

        # Create Questions CRUD Lambda
        self.questionsCrudLambda = lambda_.Function(
            self, "QuestionsCrudLambda",
            code=lambda_.Code.from_asset(".././lambda/questions_crud"),
            handler="index.lambda_handler",
            runtime=lambda_.Runtime.PYTHON_3_10,
            environment={
                "QUESTIONS_TABLE_NAME": questions_table.table_name
            },
            timeout=Duration.seconds(30)
        )

        # Grant Questions CRUD Lambda permissions to interact with DynamoDB table
        questions_table.grant_read_write_data(self.questionsCrudLambda)

        # Cognito Authorizer for API Gateway
        self.authorizer = apigateway.CognitoUserPoolsAuthorizer(
            self, "APIGatewayAuthorizer",
            cognito_user_pools=[user_pool]
        )

        # Create API Gateway
        self.api_gateway_rest_api = apigateway.RestApi(
            self, "ApiGateway",
            rest_api_name="AWS Certification Tutor API",
            description="API for AWS Certification Tutor",
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=["http://localhost:5173", frontend_url],
                allow_methods=apigateway.Cors.ALL_METHODS,
                allow_headers=["Content-Type", "Authorization",
                               "X-Amz-Date", "X-Api-Key"],
                allow_credentials=True
            )
        )

        # Create API resources
        documents_resource = self.api_gateway_rest_api.root.add_resource(
            "documents")
        questions_resource = self.api_gateway_rest_api.root.add_resource(
            "questions")

        # Document CRUD endpoints
        documents_resource.add_method(
            "GET",
            apigateway.LambdaIntegration(self.documentCrudLambda),
            authorizer=self.authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO
        )
        documents_resource.add_method(
            "POST",
            apigateway.LambdaIntegration(self.documentCrudLambda),
            authorizer=self.authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO
        )
        document_resource = documents_resource.add_resource("{document_id}")
        document_resource.add_method(
            "GET",
            apigateway.LambdaIntegration(self.documentCrudLambda),
            authorizer=self.authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO
        )
        document_resource.add_method(
            "DELETE",
            apigateway.LambdaIntegration(self.documentCrudLambda),
            authorizer=self.authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO
        )

        # Questions CRUD endpoints
        questions_resource.add_method(
            "GET",
            apigateway.LambdaIntegration(self.questionsCrudLambda),
            authorizer=self.authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO
        )
        questions_resource.add_method(
            "POST",
            apigateway.LambdaIntegration(self.questionsCrudLambda),
            authorizer=self.authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO
        )
        question_resource = questions_resource.add_resource("{question_id}")
        question_resource.add_method(
            "GET",
            apigateway.LambdaIntegration(self.questionsCrudLambda),
            authorizer=self.authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO
        )
        question_resource.add_method(
            "PUT",
            apigateway.LambdaIntegration(self.questionsCrudLambda),
            authorizer=self.authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO
        )
        question_resource.add_method(
            "DELETE",
            apigateway.LambdaIntegration(self.questionsCrudLambda),
            authorizer=self.authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO
        )

        CfnOutput(
            self, "DocumentProcessingLambdaFunctionName",
            value=self.documentProcessingLambda.function_name,
            description="Name of the document processing Lambda function"
        )

        CfnOutput(
            self, "QuestionGenerationLambdaFunctionName",
            value=self.questionGenerationLambda.function_name,
            description="Name of the question generation Lambda function"
        )

        CfnOutput(
            self, "QuestionStoringLambdaFunctionName",
            value=self.questionStoringLambda.function_name,
            description="Name of the question storing Lambda function"
        )

        CfnOutput(
            self, "DocumentCrudLambdaFunctionName",
            value=self.documentCrudLambda.function_name,
            description="Name of the document CRUD Lambda function"
        )

        CfnOutput(
            self, "QuestionsCrudLambdaFunctionName",
            value=self.questionsCrudLambda.function_name,
            description="Name of the questions CRUD Lambda function"
        )

        CfnOutput(
            self, "ApiGatewayUrl",
            value=self.api_gateway_rest_api.url,
            description="URL of the API Gateway"
        )
