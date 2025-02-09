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
  public readonly sourceDocumentsBucket: s3.Bucket;
  public readonly questionsTable: dynamodb.Table;

  constructor(scope: Construct, id: string) {
    super(scope, id);

    this.sourceDocumentsBucket = new s3.Bucket(this, "SourceDocumentsBucket", {
      versioned: true,
      encryption: s3.BucketEncryption.S3_MANAGED,
      removalPolicy: RemovalPolicy.DESTROY,
      autoDeleteObjects: true,
    });

    this.questionsTable = new dynamodb.Table(this, "QuestionsTable", {
      partitionKey: { name: "id", type: dynamodb.AttributeType.STRING },
    });
    
  }
}
