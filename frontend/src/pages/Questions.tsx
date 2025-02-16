import { Trash2 } from "lucide-react";
import DynamicTable, { ColumnConfig } from "../components/DynamicTable";

interface Question {
  questionId: string;
  topic: string;
  subtopic: string;
  questionText: string;
  options: {
    optionId: string;
    optionText: string;
    explanation: string;
  }[];
  correctOptions: string[];
  difficulty: number;
  tags: string[];
  created_at: string;
  updated_at: string;
}

const Questions = () => {
  const data: Question[] = [
    {
      questionId: "fhae23g1jj1kds1498fdjnvk342",
      topic: "IAM",
      subtopic: "IAM Policies",
      questionText:
        "Which of the following are valid ways to grant permissions in AWS IAM?",
      options: [
        {
          optionId: "A",
          optionText: "Attaching policies to users",
          explanation: "Correct. Policies can be directly attached to users.",
        },
        {
          optionId: "B",
          optionText: "Attaching policies to groups",
          explanation:
            "Correct. Policies can be attached to groups, and users inherit those permissions.",
        },
        {
          optionId: "C",
          optionText: "Attaching policies to roles",
          explanation:
            "Correct. Policies can be attached to roles, which can then be assumed by users or services.",
        },
        {
          optionId: "D",
          optionText: "Adding users directly to S3 buckets",
          explanation:
            "Incorrect.  S3 bucket policies are used for this, not direct user attachments.",
        },
      ],
      correctOptions: ["A", "B", "C"],
      difficulty: 2,
      tags: ["IAM", "Policies", "Permissions"],
      created_at: "2024-11-21T10:00:00Z",
      updated_at: "2024-11-21T10:00:00Z",
    },
  ];

  const columns: ColumnConfig[] = [
    {
      key: "questionText",
      header: "Question",
      searchable: true,
      render: (value: any) => <span className="font-medium">{value}</span>,
    },
    {
      key: "topic",
      header: "Topic",
      searchable: true,
      render: (value: any) => (
        <span className="font-semibold text-blue-600">{value}</span>
      ),
    },
    {
      key: "difficulty",
      header: "Difficulty",
      searchable: true,
      render: (value: any) => (
        <span className="font-semibold text-blue-600">{value}</span>
      ),
    },
    {
      key: "actions",
      header: "Actions",
      render: (_: any, rowData: any) => (
        <button
          onClick={() => alert(`Editing user: ${rowData.questionId}`)}
          className="text-gray-300 rounded hover:text-red-600"
        >
          <Trash2 size={24} />
        </button>
      ),
    },
  ];

  return (
    <div className="flex flex-col flex-grow">
      <header className="bg-white shadow-md p-4">
        <h1 className="text-2xl font-bold text-center">Question List</h1>
      </header>
      <div className="flex-grow p-4">
        <DynamicTable data={data} columns={columns} />
      </div>
    </div>
  );
};

export default Questions;
