from constructs import Construct
from aws_cdk import (
    RemovalPolicy,
    Duration,
    CfnOutput,
    DockerImage,
    aws_apigateway as apigateway,
    aws_lambda as lambda_,
    aws_s3 as s3,
    aws_amplify as amplify,
    aws_iam as iam,
    aws_cognito as cognito,
    aws_dynamodb as dynamodb,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as cloudfront_origins,
    aws_s3_deployment as s3_deployment,
)


class FrontendConstruct(Construct):
    frontendBucket: s3.Bucket
    frontendDistribution: cloudfront.Distribution
    identity_pool: cognito.CfnIdentityPool

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        api_gateway_rest_api: apigateway.RestApi,
        source_documents_bucket: s3.Bucket,
        questions_table: dynamodb.Table,
        user_pool: cognito.UserPool,
        user_pool_client: cognito.UserPoolClient,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create S3 bucket for static web app
        self.frontendBucket = s3.Bucket(
            self, "FrontendBucket",
            versioned=True,
            encryption=s3.BucketEncryption.S3_MANAGED,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )

        # Create an Origin Access Identity
        origin_access_identity = cloudfront.OriginAccessIdentity(
            self, "OriginAccessIdentity",
            comment="OAI for Frontend Bucket"
        )

        # Grant the OAI read permissions to the S3 bucket
        self.frontendBucket.grant_read(origin_access_identity)

        # Create a CloudFront distribution
        self.frontendDistribution = cloudfront.Distribution(
            self, "FrontendDistribution",
            default_behavior=cloudfront.BehaviorOptions(
                origin=cloudfront_origins.S3Origin(
                    self.frontendBucket, origin_access_identity=origin_access_identity)
            ),
            error_responses=[
                cloudfront.ErrorResponse(
                    http_status=403,
                    response_http_status=200,
                    response_page_path="/index.html"
                ),
                cloudfront.ErrorResponse(
                    http_status=404,
                    response_http_status=200,
                    response_page_path="/index.html"
                )
            ]
        )

        # Create Cognito Identity Pool
        self.identity_pool = cognito.CfnIdentityPool(
            self, "IdentityPool",
            allow_unauthenticated_identities=False,
            cognito_identity_providers=[
                cognito.CfnIdentityPool.CognitoIdentityProviderProperty(
                    client_id=user_pool_client.user_pool_client_id,
                    provider_name=user_pool.user_pool_provider_name
                )
            ]
        )

        # IAM Role for Authenticated Users
        authenticated_role = iam.Role(
            self, "AuthenticatedUserRole",
            assumed_by=iam.FederatedPrincipal(
                "cognito-identity.amazonaws.com",
                conditions={
                    "StringEquals": {
                        "cognito-identity.amazonaws.com:aud": self.identity_pool.ref
                    },
                    "ForAnyValue:StringLike": {
                        "cognito-identity.amazonaws.com:amr": "authenticated"
                    }
                },
                assume_role_action="sts:AssumeRoleWithWebIdentity"
            )
        )

        # Grant API Gateway Invoke Permissions
        authenticated_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "execute-api:Invoke",
                    "execute-api:ManageConnections"
                ],
                resources=[
                    f"arn:aws:execute-api:{scope.region}:{scope.account}:{api_gateway_rest_api.rest_api_id}/*/*/*"
                ]
            )
        )

        # Grant S3 read permissions to authenticated users
        authenticated_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "s3:GetObject",
                    "s3:ListBucket"
                ],
                resources=[
                    source_documents_bucket.bucket_arn,
                    f"{source_documents_bucket.bucket_arn}/*"
                ]
            )
        )

        # Attach roles to Identity Pool
        cognito.CfnIdentityPoolRoleAttachment(
            self, "IdentityPoolRoleAttachment",
            identity_pool_id=self.identity_pool.ref,
            roles={
                "authenticated": authenticated_role.role_arn
            }
        )

        # Deploy Frontend assets to S3
        frontend_deployment = s3_deployment.BucketDeployment(
            self, "FrontendDeployment",
            sources=[s3_deployment.Source.asset("../frontend/dist")],
            destination_bucket=self.frontendBucket,
            distribution=self.frontendDistribution,
            distribution_paths=["/*"],
            memory_limit=512
        )
