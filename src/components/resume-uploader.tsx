'use client';

import { useState, ChangeEvent } from 'react';
import { ref, uploadBytes, getDownloadURL } from 'firebase/storage';
import { storage } from '@/lib/firebase-client';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

export default function ResumeUploader() {
  const { user } = useAuth();
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (!selectedFile) {
      setFile(null);
      return;
    }

    const allowedTypes = [
      'application/pdf',
      'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    ];

    if (allowedTypes.includes(selectedFile.type)) {
      setFile(selectedFile);
      setMessage(null);
    } else {
      setFile(null);
      setMessage('Please select a valid PDF or Word document (.pdf, .doc, .docx).');
    }
  };

  const handleUpload = async () => {
    console.log('handleUpload called');
    console.log('User object:', user);
    console.log('File object:', file);
    if (!file || !user) {
      setMessage('Please log in and select a file first.');
      console.error('User or file is missing.');
      return;
    }

    setUploading(true);
    setMessage(`Uploading ${file.name}...`);

    // Store under raw-resumes, include uid and timestamp for uniqueness
    const storageRef = ref(
      storage,
      `raw-resumes/${user.uid}/${Date.now()}-${file.name}`
    );

    try {
      console.debug('[ResumeUploader] Attempting to upload file to:', storageRef.fullPath);
      const uploadTask = await uploadBytes(storageRef, file);
      console.debug('[ResumeUploader] uploadBytes result:', uploadTask);
      console.debug(
        '[ResumeUploader] uploadBytes ref.fullPath:',
        uploadTask.ref.fullPath,
        'bucket:',
        uploadTask.ref.bucket
      );
      const downloadUrl = await getDownloadURL(uploadTask.ref);
      console.debug('[ResumeUploader] File available at download URL:', downloadUrl);
      setMessage('Upload successful! Your resume is being processed.');
      setFile(null);
    } catch (error) {
      console.error('Upload failed:', error);
      setMessage('Upload failed. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-2">
      <h3 className="font-semibold">Upload Your Resume</h3>
      <Input type="file" accept=".pdf,.doc,.docx" onChange={handleFileChange} />
      <Button onClick={handleUpload} disabled={!file || uploading}>
        {uploading ? 'Uploading...' : 'Upload'}
      </Button>
      {message && <p className="text-sm">{message}</p>}
    </div>
  );
}