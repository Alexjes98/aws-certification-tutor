from constructs import Construct
from aws_cdk import (
    CfnOutput,
    aws_cognito as cognito,
)

class AuthConstruct(Construct):
    user_pool: cognito.UserPool
    user_pool_client: cognito.UserPoolClient
    identity_pool: cognito.CfnIdentityPool
    
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
         # Cognito User Pool
        self.user_pool = cognito.UserPool(
            self, "CTUserPool",
            user_pool_name="CTUserPool",
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

        # Cognito User Pool Client with temporary URLs
        self.user_pool_client = self.user_pool.add_client(
            "WebAppUserPoolClient",
            auth_flows=cognito.AuthFlow(
                admin_user_password=True,
                user_password=True,
                custom=True,
                user_srp=True
            ),
            o_auth=cognito.OAuthSettings(
                callback_urls=["http://localhost:5173"],
                logout_urls=["http://localhost:5173"]
            )
        )
        
        # Create Cognito Identity Pool
        self.identity_pool = cognito.CfnIdentityPool(
            self, "IdentityPool",
            allow_unauthenticated_identities=False,
            cognito_identity_providers=[
                cognito.CfnIdentityPool.CognitoIdentityProviderProperty(
                    client_id=self.user_pool_client.user_pool_client_id,
                    provider_name=self.user_pool.user_pool_provider_name
                )
            ]
        )
        
        CfnOutput(
            self, "UserPoolId",
            value=self.user_pool.user_pool_id
        )
        
        CfnOutput(
            self, "UserPoolClientId",
            value=self.user_pool_client.user_pool_client_id
        )
        
        CfnOutput(
            self, "IdentityPoolId",
            value=self.identity_pool.ref
        )
            
