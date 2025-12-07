import os
from typing import Optional, BinaryIO

class CloudAdapter:
    """
     Unified interface for Cloud Object Storage (S3, Azure Blob).
    """
    def __init__(self, provider: str, bucket_name: str, connection_string: Optional[str] = None):
        self.provider = provider.lower()
        self.bucket_name = bucket_name
        self.connection_string = connection_string or os.getenv("CLOUD_STORAGE_CONN_STR")
        
        self.s3_client = None
        self.blob_service_client = None
        
        self._initialize_client()

    def _initialize_client(self):
        if self.provider == "s3":
            try:
                import boto3
                self.s3_client = boto3.client('s3')
            except ImportError:
                print("Warning: boto3 not installed. S3 features unavailable.")
                
        elif self.provider == "azure":
            try:
                from azure.storage.blob import BlobServiceClient
                if self.connection_string:
                    self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
            except ImportError:
                print("Warning: azure-storage-blob not installed. Azure features unavailable.")

    def upload_file(self, file_path: str, object_name: Optional[str] = None):
        object_name = object_name or os.path.basename(file_path)
        
        if self.provider == "s3" and self.s3_client:
            self.s3_client.upload_file(file_path, self.bucket_name, object_name)
            return f"s3://{self.bucket_name}/{object_name}"
            
        elif self.provider == "azure" and self.blob_service_client:
            blob_client = self.blob_service_client.get_blob_client(container=self.bucket_name, blob=object_name)
            with open(file_path, "rb") as data:
                blob_client.upload_blob(data, overwrite=True)
            return blob_client.url
            
        else:
            raise NotImplementedError(f"Provider {self.provider} not fully initialized or supported.")

    def download_file(self, object_name: str, dest_path: str):
        if self.provider == "s3" and self.s3_client:
            self.s3_client.download_file(self.bucket_name, object_name, dest_path)
            
        elif self.provider == "azure" and self.blob_service_client:
            blob_client = self.blob_service_client.get_blob_client(container=self.bucket_name, blob=object_name)
            with open(dest_path, "wb") as download_file:
                download_file.write(blob_client.download_blob().readall())
        else:
            raise NotImplementedError(f"Provider {self.provider} not fully initialized or supported.")
