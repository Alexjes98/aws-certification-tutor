import { Construct } from "constructs";
import {
  RemovalPolicy,
  Duration,
  aws_dynamodb as dynamodb,
  aws_s3 as s3,
  aws_sqs as sqs,
} from "aws-cdk-lib";
import * as lambda from "aws-cdk-lib/aws-lambda";
import * as apigateway from "aws-cdk-lib/aws-apigateway";
import * as iam from "aws-cdk-lib/aws-iam";
import * as s3n from 'aws-cdk-lib/aws-s3-notifications';
import * as sfn from 'aws-cdk-lib/aws-stepfunctions';
import * as tasks from 'aws-cdk-lib/aws-stepfunctions-tasks';
import * as lambdaEventSources from 'aws-cdk-lib/aws-lambda-event-sources';

export class BackendConstruct extends Construct {
  public readonly sourceDocumentsBucket: s3.Bucket;
  public readonly questionsTable: dynamodb.Table;
  public readonly pdfProcessingQueue: sqs.Queue;
  public readonly pdfProcessorLambda: lambda.DockerImageFunction;
  public readonly pdfProcessingStateMachine: sfn.StateMachine;
  public readonly sqsTriggerLambda: lambda.Function;

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
      removalPolicy: RemovalPolicy.DESTROY,
    });

    // Create dead letter queue
    const deadLetterQueue = new sqs.Queue(this, 'PdfProcessingQueueDLQ', {
      visibilityTimeout: Duration.seconds(300),
      retentionPeriod: Duration.days(14),
      removalPolicy: RemovalPolicy.DESTROY,
    });

    // Create SQS Queue for PDF processing
    this.pdfProcessingQueue = new sqs.Queue(this, 'PdfProcessingQueue', {
      visibilityTimeout: Duration.seconds(300),
      retentionPeriod: Duration.days(14),
      removalPolicy: RemovalPolicy.DESTROY,
      deadLetterQueue: {
        queue: deadLetterQueue,
        maxReceiveCount: 3,
      },
    });

    // Create Docker Lambda function for PDF processing
    this.pdfProcessorLambda = new lambda.Function(this, 'PdfExtractionLambda', {
      code: lambda.Code.fromAsset('../lambda/pdf_extraction'),
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: 'index.lambda_handler',
      timeout: Duration.seconds(300),
      memorySize: 512,
      environment: {
        QUESTIONS_TABLE: this.questionsTable.tableName,
        SQS_QUEUE_URL: this.pdfProcessingQueue.queueUrl,
      },
    });

    // Grant permissions
    this.sourceDocumentsBucket.grantRead(this.pdfProcessorLambda);
    this.questionsTable.grantWriteData(this.pdfProcessorLambda);
    this.pdfProcessingQueue.grantConsumeMessages(this.pdfProcessorLambda);

    // Add SQS queue as destination for PDF uploads
    this.sourceDocumentsBucket.addEventNotification(
      s3.EventType.OBJECT_CREATED,
      new s3n.SqsDestination(this.pdfProcessingQueue),
      { suffix: '.pdf' }
    );

    // Create Step Functions workflow
    const pdfExtractionTask = new tasks.LambdaInvoke(this, 'PdfExtractionTask', {
      lambdaFunction: this.pdfProcessorLambda,
      resultPath: '$.extractionResult',
    });

    this.pdfProcessingStateMachine = new sfn.StateMachine(this, 'PdfProcessingWorkflow', {
      definitionBody: sfn.DefinitionBody.fromChainable(pdfExtractionTask),
      timeout: Duration.minutes(30),
    });

    // Create Lambda function to trigger Step Functions from SQS
    this.sqsTriggerLambda = new lambda.Function(this, 'SqsToStepFunctionsHandler', {
      runtime: lambda.Runtime.NODEJS_18_X,
      handler: 'index.handler',
      code: lambda.Code.fromInline(`
        const AWS = require('aws-sdk');
        const stepfunctions = new AWS.StepFunctions();
        
        exports.handler = async (event) => {
          const records = event.Records;
          const stateMachineArn = process.env.STATE_MACHINE_ARN;
          
          await Promise.all(records.map(record => {
            const input = {
              stateMachineArn,
              input: JSON.stringify({
                messageBody: JSON.parse(record.body),
                messageId: record.messageId
              })
            };
            
            return stepfunctions.startExecution(input).promise();
          }));
        };
      `),
      environment: {
        STATE_MACHINE_ARN: this.pdfProcessingStateMachine.stateMachineArn,
      },
      timeout: Duration.minutes(1),
    });

    // Add SQS trigger to Lambda
    this.sqsTriggerLambda.addEventSource(new lambdaEventSources.SqsEventSource(this.pdfProcessingQueue));

    // Grant permissions for Lambda to start Step Functions execution
    this.pdfProcessingStateMachine.grantStartExecution(this.sqsTriggerLambda);
  }
}
