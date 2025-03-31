import { useState, useEffect } from "react";

import DynamicTable, { ColumnConfig } from "../components/DynamicTable";
import { Trash2, Upload, RefreshCcw } from "lucide-react";
import { Document, getDocuments, uploadDocument, deleteDocument } from "../api/documents";

export default function Documents() {
  const [searchTerm, setSearchTerm] = useState("");
  const [documents, setDocuments] = useState<Document[]>([{"document_id": "inttroductiontochessbasicrulesandtips.pdf", "size": 47075, "last_modified": "2025-03-30T21:48:02+00:00", "metadata": {}}]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchDocuments = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await getDocuments();
      setDocuments(data);
    } catch (error) {
      setError('Failed to fetch documents. Please try again.');
      console.error('Error fetching documents:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      try {
        setIsLoading(true);
        setError(null);
        await uploadDocument(file);
        await fetchDocuments();
      } catch (error) {
        setError('Failed to upload document. Please try again.');
        console.error('Error uploading document:', error);
      } finally {
        setIsLoading(false);
      }
    }
  };

  const handleDelete = async (documentId: string) => {
    if (window.confirm('Are you sure you want to delete this document?')) {
      try {
        setIsLoading(true);
        setError(null);
        await deleteDocument(documentId);
        await fetchDocuments();
      } catch (error) {
        setError('Failed to delete document. Please try again.');
        console.error('Error deleting document:', error);
      } finally {
        setIsLoading(false);
      }
    }
  };

  const handleRefresh = async () => {
    try {
      setIsLoading(true);
      setError(null);
      await fetchDocuments();
    } catch (error) {
      setError('Failed to refresh documents. Please try again.');
      console.error('Error refreshing documents:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const columns: ColumnConfig[] = [
    {
      key: "documentId",
      header: "Document ID",
      searchable: true,
      render: (value: string) => <span className="font-medium">{value}</span>,
    },
    {
      key: "fileName",
      header: "File Name",
      searchable: true,
      render: (value: string) => <span className="font-medium">{value}</span>,
    },
    {
      key: "createdAt",
      header: "Created At",
      searchable: true,
      render: (value: string) => (
        <span className="font-semibold text-blue-600">
          {new Date(value).toLocaleString()}
        </span>
      ),
    },
    {
      key: "updatedAt",
      header: "Updated At",
      searchable: true,
      render: (value: string) => (
        <span className="font-semibold text-blue-600">
          {new Date(value).toLocaleString()}
        </span>
      ),
    },
    {
      key: "actions",
      header: "Actions",
      render: (_: any, rowData: Document) => (
        <button
          onClick={() => handleDelete(rowData.document_id)}
          className="text-gray-300 rounded hover:text-red-600"
          disabled={isLoading}
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
        {error && (
          <div className="mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded">
            {error}
          </div>
        )}
        <div className="flex justify-between mb-4">
          <input
            type="text"
            placeholder="Search"
            className="border border-gray-300 rounded-md px-4 py-2"
            onChange={(e) => setSearchTerm(e.target.value)}
            disabled={isLoading}
          />
          <div className="flex gap-2">
            <button 
              className="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
              onClick={handleRefresh}
              disabled={isLoading}
            >
              <RefreshCcw size={24} />
            </button>
            <label className="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer">
              <input
                type="file"
                className="hidden"
                onChange={handleFileUpload}
                disabled={isLoading}
              />
              <Upload size={24} />
            </label>
          </div>
        </div>
        <div className="flex-grow">
          <DynamicTable
            data={documents}
            columns={columns}
            externalSearchTerm={searchTerm}
            isLoading={isLoading}
          />
        </div>
      </div>
    </div>
  );
}
