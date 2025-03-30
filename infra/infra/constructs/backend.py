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
    aws_apigateway as apigateway,
    aws_cognito as cognito,
)
from aws_cdk.aws_lambda import DockerImageFunction, DockerImageCode, Function


class BackendConstruct(Construct):
    sourceDocumentsBucket: s3.Bucket
    documentProcessingLambda: DockerImageFunction
    questionGenerationLambda: DockerImageFunction
    questionStoringLambda: Function
    questionsTable: dynamodb.Table
    api_gateway_rest_api: apigateway.RestApi
    documentCrudLambda: lambda_.Function
    questionsCrudLambda: lambda_.Function
    user_pool: cognito.UserPool
    user_pool_client: cognito.UserPoolClient
    authorizer: apigateway.CognitoUserPoolsAuthorizer
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
        
        # Create Document CRUD Lambda
        self.documentCrudLambda = lambda_.Function(
            self, "DocumentCrudLambda",
            code=lambda_.Code.from_asset(".././lambda/document_crud"),
            handler="index.lambda_handler",
            runtime=lambda_.Runtime.PYTHON_3_10,
            environment={
                "SOURCE_BUCKET_NAME": self.sourceDocumentsBucket.bucket_name
            },
            timeout=Duration.seconds(30)
        )

        # Grant Document CRUD Lambda permissions to interact with S3 bucket
        self.sourceDocumentsBucket.grant_read_write(self.documentCrudLambda)

        # Create Questions CRUD Lambda
        self.questionsCrudLambda = lambda_.Function(
            self, "QuestionsCrudLambda",
            code=lambda_.Code.from_asset(".././lambda/questions_crud"),
            handler="index.lambda_handler",
            runtime=lambda_.Runtime.PYTHON_3_10,
            environment={
                "QUESTIONS_TABLE_NAME": self.questionsTable.table_name
            },
            timeout=Duration.seconds(30)
        )

        # Grant Questions CRUD Lambda permissions to interact with DynamoDB table
        self.questionsTable.grant_read_write_data(self.questionsCrudLambda)
        
        # Cognito User Pool
        self.user_pool = cognito.UserPool(
            self, "WebAppUserPool",
            user_pool_name="WebAppUserPool",
            self_sign_up_enabled=True,
            sign_in_aliases=cognito.SignInAliases(
                email=True,
                username=True
            ),
            standard_attributes=cognito.StandardAttributes(
                email=cognito.StandardAttribute(required=True, mutable=True)
            ),
            password_policy=cognito.PasswordPolicy(
                min_length=8,
                require_lowercase=True,
                require_digits=True,
                require_uppercase=True,
                require_symbols=True
            ),
            account_recovery=cognito.AccountRecovery.EMAIL_ONLY
        )
        
        # Cognito User Pool Client
        self.user_pool_client = self.user_pool.add_client(
            "WebAppUserPoolClient",
            auth_flows=cognito.AuthFlow(
                admin_user_password=True,
                user_password=True,
                custom=True,
                user_srp=True
            ),
            o_auth=cognito.OAuthSettings(
                callback_urls=["http://localhost:3000", "https://yourdomain.com"],
                logout_urls=["http://localhost:3000", "https://yourdomain.com"]
            )
        )
        
        # Cognito Authorizer for API Gateway
        self.authorizer = apigateway.CognitoUserPoolsAuthorizer(
            self, "APIGatewayAuthorizer",
            cognito_user_pools=[self.user_pool]
        )
        
        # Create API Gateway
        self.api_gateway_rest_api = apigateway.RestApi(
            self, "ApiGateway",
            rest_api_name="AWS Certification Tutor API",
            description="API for AWS Certification Tutor",
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=apigateway.Cors.ALL_ORIGINS,
                allow_methods=apigateway.Cors.ALL_METHODS,
                allow_headers=["Content-Type", "Authorization", "X-Amz-Date", "X-Api-Key"]
            )
        )

        # Create API resources
        documents_resource = self.api_gateway_rest_api.root.add_resource("documents")
        questions_resource = self.api_gateway_rest_api.root.add_resource("questions")

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