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
    frontendDistribution: cloudfront.Distribution
    origin_access_identity: cloudfront.OriginAccessIdentity
    authenticated_role: iam.Role

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        frontend_bucket: s3.Bucket,
        source_documents_bucket: s3.Bucket,
        identity_pool: cognito.CfnIdentityPool,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create an Origin Access Identity
        self.origin_access_identity = cloudfront.OriginAccessIdentity(
            self, "OriginAccessIdentity",
            comment="OAI for Frontend Bucket"
        )

        # Grant the OAI read permissions to the S3 bucket
        frontend_bucket.grant_read(self.origin_access_identity)

        # Create a CloudFront distribution
        self.frontendDistribution = cloudfront.Distribution(
            self, "FrontendDistribution",
            default_behavior=cloudfront.BehaviorOptions(
                origin=cloudfront_origins.S3Origin(
                    frontend_bucket, origin_access_identity=self.origin_access_identity)
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
        # IAM Role for Authenticated Users
        self.authenticated_role = iam.Role(
            self, "AuthenticatedUserRole",
            assumed_by=iam.FederatedPrincipal(
                "cognito-identity.amazonaws.com",
                conditions={
                    "StringEquals": {
                        "cognito-identity.amazonaws.com:aud": identity_pool.ref
                    },
                    "ForAnyValue:StringLike": {
                        "cognito-identity.amazonaws.com:amr": "authenticated"
                    }
                },
                assume_role_action="sts:AssumeRoleWithWebIdentity"
            )
        )

        # Grant S3 read permissions to authenticated users
        self.authenticated_role.add_to_policy(
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
            identity_pool_id=identity_pool.ref,
            roles={
                "authenticated": self.authenticated_role.role_arn
            }
        )

        # Deploy Frontend assets to S3
        frontend_deployment = s3_deployment.BucketDeployment(
            self, "FrontendDeployment",
            sources=[s3_deployment.Source.asset("../frontend/dist")],
            destination_bucket=frontend_bucket,
            distribution=self.frontendDistribution,
            distribution_paths=["/*"],
            memory_limit=512
        )
        
        CfnOutput(
            self, "FrontendDistributionDomainName",
            value=self.frontendDistribution.domain_name,
            description="Domain name of the frontend distribution"
        )
        
        CfnOutput(
            self, "FrontendDistributionId",
            value=self.frontendDistribution.distribution_id,
            description="ID of the frontend distribution"
        )
