from aws_cdk import (
    Stack,
    aws_iam as iam,
)
from constructs import Construct
from .constructs.backend import BackendConstruct
from .constructs.frontend import FrontendConstruct
from .constructs.storage import StorageConstruct
from .constructs.auth import AuthConstruct

class InfraStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        #TODO: Add Amplify authenticator to the frontend react app

        # Create the storage construct
        storage = StorageConstruct(self, "CertificationTutorStorage")
        
        # Create the auth construct
        auth = AuthConstruct(self, "CertificationTutorAuth")
        
        # Create the frontend construct
        frontend = FrontendConstruct(
            self, "CertificationTutorFrontend",
            frontend_bucket=storage.frontendBucket,
            source_documents_bucket=storage.sourceDocumentsBucket,
            identity_pool=auth.identity_pool
        )
        #FRONTEND CONTRUSCT IS GENERATING A THINK CALLED CUSOTM RESOURCE 512 MiB AND MAKES FAILS WHEN DESTROYING THE STACK
        #INVESTIGATE WHY THIS IS HAPPENING
        
        # Create the backend construct
        backend = BackendConstruct(
            self, "CertificationTutorBackend",
            source_documents_bucket=storage.sourceDocumentsBucket,
            questions_table=storage.questionsTable,
            user_pool=auth.user_pool,
            frontend_url=f"https://{frontend.frontendDistribution.distribution_domain_name}"
        )
        
        #Aditional Configurations for resources to work together
        
        #THIS IS NOT WORKING SEARCH HOW TO DO THIS BECAUSE  RIGHT NOW IS NOT BRAKES ALL THE DEPLOYMENT
        #IS IT MAYBE THE FACT THAT IS OUTSIDE THE FRONTEND OR THAT SOMETHING IN THE POLICY IS NOT CORRECT
        # Update frontend with API Gateway permissions
        #frontend.authenticated_role.add_to_policy(
        #    iam.PolicyStatement(
        #        effect=iam.Effect.ALLOW,
        #        actions=[
        #            "execute-api:Invoke",
        #            "execute-api:ManageConnections"
        #        ],
        #        resources=[
        #            f"arn:aws:execute-api:{scope.region}:{scope.account}:{backend.api_gateway_rest_api.rest_api_id}/*"
        #        ]
        #    )
        #)
