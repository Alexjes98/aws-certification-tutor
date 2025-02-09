import * as cdk from "aws-cdk-lib";
import {
  CfnOutput
} from "aws-cdk-lib";
import { Construct } from "constructs";
import { BackendConstruct } from "./constructs/backend";
export class CdkStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // The code that defines your stack goes here
    const backend = new BackendConstruct(this, "BackendConstruct");

    // Outputs (optional, helpful for testing)
    new CfnOutput(this, "StackRegion", {
      value: this.region,
    });

    new CfnOutput(this, "SourceDocumentsBucket", {
      value: backend.sourceDocumentsBucket.bucketName,
    });

    new CfnOutput(this, "QuestionsTable", {
      value: backend.questionsTable.tableName,
    });
    
  }
}
