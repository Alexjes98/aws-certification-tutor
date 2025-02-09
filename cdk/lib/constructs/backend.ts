import { Construct } from "constructs";
import {
  RemovalPolicy,
  aws_dynamodb as dynamodb,
  aws_s3 as s3,
} from "aws-cdk-lib";
import * as lambda from "aws-cdk-lib/aws-lambda";
import * as apigateway from "aws-cdk-lib/aws-apigateway";
import * as iam from "aws-cdk-lib/aws-iam";

export class BackendConstruct extends Construct {
  public readonly api: apigateway.LambdaRestApi;

  constructor(scope: Construct, id: string, frontendBucketArn: string) {
    super(scope, id);

    const sourceDocumentsBucket = new s3.Bucket(this, "SourceDocumentsBucket", {
      versioned: true,
      encryption: s3.BucketEncryption.S3_MANAGED,
      removalPolicy: RemovalPolicy.DESTROY,
      autoDeleteObjects: true,
    });

    const questionsTable = new dynamodb.Table(this, "QuestionsTable", {
      partitionKey: { name: "id", type: dynamodb.AttributeType.STRING },
    });
    
  }
}
