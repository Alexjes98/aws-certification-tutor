{
  "schema": {
    "type": "object",
    "properties": {
      "questionId": {
        "type": "string",
        "description": "Unique identifier for the question (UUID recommended)"
      },
      "topic": {
        "type": "string",
        "description": "Topic of the question (e.g., 'EC2', 'Lambda', 'Security')"
      },
      "subtopic": {
        "type": "string",
        "description": "Optional subtopic for finer categorization (e.g., 'EC2 Networking', 'Lambda Concurrency')"
      },
      "questionText": {
        "type": "string",
        "description": "The actual question text"
      },
      "options": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "optionId": {
              "type": "string",
              "description": "Unique identifier for the option (A, B, C, D, etc.)"
            },
            "optionText": {
              "type": "string",
              "description": "Text of the answer option"
            },
            "explanation": {
              "type": "string",
              "description": "Explanation of why this option is correct/incorrect"
            }
          },
          "required": [
            "optionId",
            "optionText",
            "explanation"
          ]
        },
        "minItems": 2,
        "uniqueItems": true,
        "description": "Array of answer options"
      },
      "correctOptions": {
        "type": "array",
        "items": {
          "type": "string"
        },
        "description": "Array of optionIds that are correct (e.g., ['A', 'C'])",
        "minItems": 1 
      },
      "difficulty": {
        "type": "integer",
        "description": "Difficulty level of the question (e.g., 1-Easy, 2-Medium, 3-Hard)"
      },
      "tags": {
        "type": "array",
        "items": {
          "type": "string"
        },
        "description": "Array of tags for further filtering and categorization (e.g., ['IAM', 'Policy', 'Role'])"
      },
      "created_at": {
        "type": "string",
        "format": "date-time",
        "description": "Timestamp of question creation"
      },
      "updated_at": {
        "type": "string",
        "format": "date-time",
        "description": "Timestamp of last question update"
      }
    },
    "required": [
      "questionId",
      "topic",
      "questionText",
      "options",
      "correctOptions",
      "difficulty",
      "created_at",
      "updated_at"
    ]
  }
}

{
  "questionId": "multi-answer-question-123",
  "topic": "IAM",
  "subtopic": "IAM Policies",
  "questionText": "Which of the following are valid ways to grant permissions in AWS IAM?",
  "options": [
    { "optionId": "A", "optionText": "Attaching policies to users", "explanation": "Correct. Policies can be directly attached to users." },
    { "optionId": "B", "optionText": "Attaching policies to groups", "explanation": "Correct. Policies can be attached to groups, and users inherit those permissions." },
    { "optionId": "C", "optionText": "Attaching policies to roles", "explanation": "Correct. Policies can be attached to roles, which can then be assumed by users or services." },
    { "optionId": "D", "optionText": "Adding users directly to S3 buckets", "explanation": "Incorrect.  S3 bucket policies are used for this, not direct user attachments." }
  ],
  "correctOptions": ["A", "B", "C"],
  "difficulty": 2,
  "tags": ["IAM", "Policies", "Permissions"],
  "created_at": "2024-11-21T10:00:00Z",
  "updated_at": "2024-11-21T10:00:00Z"
}