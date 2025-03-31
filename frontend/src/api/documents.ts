const API_URL = import.meta.env.VITE_API_URL;

export interface Document {
  document_id: string;
  size: number;
  last_modified: string;
  metadata: Record<string, any>;
}

// TODO: GET https://apigategay.amazonaws.com/documents net::ERR_FAILED 403 (Forbidden)
/* TODO: Access to fetch at 'https://apigategay.us-east-1.amazonaws.com/documents'
//  from origin 'http://localhost:5173' has been blocked by CORS policy: No 'Access-Control-Allow-Origin'
//  header is present on the requested resource. If an opaque response serves your needs, set the request's 
// mode to 'no-cors' to fetch the resource with CORS disabled.

PROBABLY NEED TO ADD CORS TO THE API GATEWAY
AND GIVE AUTH USER RIGHT PERMISSIONS
*/
export const getDocuments = async (): Promise<Document[]> => {
  const response = await fetch(`${API_URL}/documents`);
  if (!response.ok) {
    throw new Error('Failed to fetch documents');
  }
  // TODO: MAP THIS TO VALUES IN THE DOCUMENT INTERFACE
  return response.json();
};

export const uploadDocument = async (file: File): Promise<Document> => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch(`${API_URL}/documents`, {
    method: 'POST',
    body: formData,
  });
  
  if (!response.ok) {
    throw new Error('Failed to upload document');
  }
  return response.json();
};

export const deleteDocument = async (documentId: string): Promise<void> => {
  const response = await fetch(`${API_URL}/documents/${documentId}`, {
    method: 'DELETE',
  });
  
  if (!response.ok) {
    throw new Error('Failed to delete document');
  }
};
