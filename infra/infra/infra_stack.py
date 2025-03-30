from aws_cdk import (
    # Duration,
    Stack,
    CfnOutput,
    # aws_sqs as sqs,
)
from constructs import Construct
from .constructs.backend import BackendConstruct
from .constructs.frontend import FrontendConstruct


class InfraStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create the backend construct
        backend = BackendConstruct(self, "Backend")

        # Create the frontend construct
        frontend = FrontendConstruct(
            self, "Frontend", api_gateway_rest_api=backend.api_gateway_rest_api,
            source_documents_bucket=backend.sourceDocumentsBucket,
            questions_table=backend.questionsTable,
            user_pool=backend.user_pool,
            user_pool_client=backend.user_pool_client
        )

        # Backend outputs
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

        # Frontend outputs
        CfnOutput(
            self, "ApiGatewayUrl",
            value=backend.api_gateway_rest_api.url,
            description="URL of the API Gateway"
        )

        CfnOutput(
            self, "DocumentCrudLambdaFunctionName",
            value=backend.documentCrudLambda.function_name,
            description="Name of the document CRUD Lambda function"
        )

        CfnOutput(
            self, "QuestionsCrudLambdaFunctionName",
            value=backend.questionsCrudLambda.function_name,
            description="Name of the questions CRUD Lambda function"
        )

        CfnOutput(
            self, "FrontendBucketName",
            value=frontend.frontendBucket.bucket_name,
            description="Name of the frontend bucket"
        )

        CfnOutput(
            self, "FrontendDistributionDomainName",
            value=frontend.frontendDistribution.domain_name,
            description="Domain name of the frontend distribution"
        )

        CfnOutput(
            self, "FrontendDistributionId",
            value=frontend.frontendDistribution.distribution_id,
            description="ID of the frontend distribution"
        )

        CfnOutput(
            self, "IdentityPoolId",
            value=frontend.identity_pool.ref,
            description="ID of the Cognito Identity Pool"
        )

