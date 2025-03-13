import React, { useState, useEffect } from "react";

import DynamicTable, { ColumnConfig } from "../components/DynamicTable";
import { Trash2, Upload, RefreshCcw } from "lucide-react";

import { S3Service } from "../api/s3_service";

interface Document {
  id: string;
  name: string;
  createdAt: string;
  updatedAt: string;
}

export default function Documents() {
  const [searchTerm, setSearchTerm] = useState("");
  const [documents, setDocuments] = useState<Document[]>([]);

  const documentsService = new S3Service("us-east-1", "your-bucket-name", {
    accessKeyId: "your-access-key-id",
    secretAccessKey: "your-secret-access-key",
    sessionToken: "your-session-token",
  });

  useEffect(() => {
    const fetchDocuments = async () => {
      const documents = await documentsService.listObjects();
      console.log(documents);
      
    };
    fetchDocuments();
  }, []);
  
  const columns: ColumnConfig[] = [
    {
      key: "documentId",
      header: "Document ID",
      searchable: true,
      render: (value: string) => <span className="font-medium">{value}</span>,
    },
    {
      key: "createdAt",
      header: "Created At",
      searchable: true,
      render: (value: any) => (
        <span className="font-semibold text-blue-600">{value}</span>
      ),
    },
    {
      key: "updatedAt",
      header: "Updated At",
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
      <div className="min-h-screen bg-gray-100 py-12 px-4 sm:px-6 lg:px-8">
        <header className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Your uploaded documents
          </h1>
          <p className="text-xl text-gray-600">
            Here you can see all the documents you have uploaded.
          </p>
        </header>
        <div className="flex justify-between mb-4">
          <input
            type="text"
            placeholder="Search"
            className="border border-gray-300 rounded-md px-4 py-2"
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          <div className="flex gap-2">
            <button className="bg-blue-500 text-white px-4 py-2 rounded-md">
              <RefreshCcw size={24} />
            </button>
          <button className="bg-blue-500 text-white px-4 py-2 rounded-md">
              <Upload size={24} />
            </button>
          </div>
        </div>
        <div className="flex-grow p-4">
          <DynamicTable data={documents} columns={columns} externalSearchTerm={searchTerm} />
        </div>
      </div>
    </div>
  );
}
