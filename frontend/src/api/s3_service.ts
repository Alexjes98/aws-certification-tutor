import { 
  S3Client, 
  GetObjectCommand, 
  ListObjectsV2Command, 
  DeleteObjectCommand, 
  PutObjectCommand,
  GetObjectCommandOutput,
  ListObjectsV2CommandOutput,
  DeleteObjectCommandOutput,
  PutObjectCommandOutput
} from '@aws-sdk/client-s3';

interface S3Credentials {
  accessKeyId: string;
  secretAccessKey: string;
  sessionToken?: string;
}

export class S3Service {
  private s3Client: S3Client;
  private bucketName: string;

  /**
   * Creates an S3Service instance
   * @param region AWS region (e.g., 'us-east-1')
   * @param bucketName Name of the S3 bucket
   * @param credentials AWS credentials
   * 
   * Credentials can be obtained from:
   * 1. AWS IAM User: accessKeyId and secretAccessKey from AWS Console
   * 2. AWS STS: Temporary credentials including sessionToken
   * 3. IAM Role: Automatically handled by AWS SDK when running on AWS services
   * 4. AWS Cognito: Temporary credentials from identity pool
   * 5. AWS SSO: Temporary credentials from SSO login
   */
  constructor(region: string, bucketName: string, credentials: S3Credentials) {
    this.s3Client = new S3Client({ 
      region,
      credentials: {
        accessKeyId: credentials.accessKeyId,
        secretAccessKey: credentials.secretAccessKey,
        ...(credentials.sessionToken && { sessionToken: credentials.sessionToken })
      }
    });
    this.bucketName = bucketName;
  }

  /**
   * Get an object from S3
   * @param key The key of the object in S3
   * @returns The object data
   */
  async getObject(key: string): Promise<GetObjectCommandOutput> {
    const command = new GetObjectCommand({
      Bucket: this.bucketName,
      Key: key,
    });

    return this.s3Client.send(command);
  }

  /**
   * List objects in a bucket
   * @param prefix Optional prefix to filter objects
   * @param maxKeys Optional maximum number of keys to return
   * @returns List of objects
   */
  async listObjects(prefix?: string, maxKeys?: number): Promise<ListObjectsV2CommandOutput> {
    const command = new ListObjectsV2Command({
      Bucket: this.bucketName,
      Prefix: prefix,
      MaxKeys: maxKeys,
    });

    return this.s3Client.send(command);
  }

  /**
   * Delete an object from S3
   * @param key The key of the object to delete
   * @returns The delete operation result
   */
  async deleteObject(key: string): Promise<DeleteObjectCommandOutput> {
    const command = new DeleteObjectCommand({
      Bucket: this.bucketName,
      Key: key,
    });

    return this.s3Client.send(command);
  }

  /**
   * Upload an object to S3
   * @param key The key for the object in S3
   * @param body The object data to upload
   * @param contentType Optional content type of the object
   * @returns The upload operation result
   */
  async putObject(
    key: string, 
    body: string | Uint8Array | Buffer, 
    contentType?: string
  ): Promise<PutObjectCommandOutput> {
    const command = new PutObjectCommand({
      Bucket: this.bucketName,
      Key: key,
      Body: body,
      ContentType: contentType,
    });

    return this.s3Client.send(command);
  }
}
