import React, { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { uploadStudentData } from '../../services/api';

interface DataUploadFormProps {
  dataType: 'attendance' | 'marks' | 'fees';
  onUploadComplete: () => void;
}

export const DataUploadForm: React.FC<DataUploadFormProps> = ({
  dataType,
  onUploadComplete
}) => {
  const [isUploading, setIsUploading] = useState(false);

  const onDrop = async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (file) {
      setIsUploading(true);
      try {
        await uploadStudentData(file, dataType);
        onUploadComplete();
      } catch (error) {
        console.error('Upload failed:', error);
      } finally {
        setIsUploading(false);
      }
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'text/csv': ['.csv']
    },
    maxFiles: 1
  });

  return (
    <div {...getRootProps()} className="dropzone">
      <input {...getInputProps()} />
      {/* Dropzone UI */}
    </div>
  );
};