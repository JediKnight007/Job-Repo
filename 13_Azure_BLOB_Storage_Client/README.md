# Azure Blob Storage Client

## Project Overview
This project implements a client library for Azure Blob Storage, providing async file upload capabilities with proper content type handling and SAS token authentication. It demonstrates cloud storage integration, Azure SDK usage, and asynchronous Python programming.

## Technical Skills Demonstrated

### Cloud Computing
- **Azure Blob Storage**: Microsoft's object storage solution
- **SAS Tokens**: Shared Access Signature authentication
- **Cloud Storage APIs**: Working with cloud provider SDKs
- **Object Storage**: Understanding blob/object storage concepts

### Python Programming
- **Async/Await**: Asynchronous programming with asyncio
- **Azure SDK**: Using azure-storage-blob library
- **Error Handling**: Proper exception handling for cloud operations
- **Type Hints**: Modern Python type annotations

### Software Engineering
- **Client Library Design**: Clean API interface
- **Authentication**: SAS token management
- **Content Types**: MIME type handling
- **Logging**: Proper logging for debugging

## Project Structure
```python
BLOB.py                 # Azure Blob Storage client implementation
└── BlobStorageClient   # Main client class
```

## Key Features

### 1. Blob Storage Client
```python
class BlobStorageClient:
    def __init__(self, account_url: str, container: str, 
                 sas_token: Optional[str] = None):
        """
        Initialize Azure Blob Storage client.
        
        Args:
            account_url: Azure storage account URL
            container: Container name
            sas_token: SAS token for authentication
        """
```

### 2. Async File Upload
```python
async def upload_file(self, object_key: str, data: Union[bytes, str],
                     mime: str = 'application/octet-stream',
                     overwrite: bool = True) -> Dict[str, Any]:
    """
    Upload file to Azure Blob Storage.
    
    Args:
        object_key: Blob name/path
        data: File content (bytes or string)
        mime: MIME type for Content-Type header
        overwrite: Whether to overwrite existing blob
        
    Returns:
        Dictionary with object_key and URL
    """
```

### 3. Content Type Support
- Automatic MIME type setting
- Proper Content-Type headers
- Support for various file types (images, documents, videos)

### 4. SAS Token Authentication
- Shared Access Signature URLs
- Secure, time-limited access
- No storage account keys in code

## Technical Implementation

### Complete Implementation
```python
from datetime import datetime, timedelta
from azure.storage.blob import (BlobServiceClient, generate_account_sas, 
                                 ResourceTypes, AccountSasPermissions)
from azure.storage.blob import ContainerClient, ContentSettings
from azure.storage.blob.aio import BlobClient
from typing import TYPE_CHECKING, Optional, Dict, Union, Any
import logging

logger = logging.getLogger(__name__)

class BlobStorageClient:
    """Azure Blob Storage client with async upload support."""
    
    def __init__(self, account_url: str, container: str, 
                 sas_token: Optional[str] = None):
        """
        Initialize Azure Blob Storage client.
        
        Args:
            account_url: Azure storage account URL 
                        (e.g., https://myaccount.blob.core.windows.net)
            container: Container name to store blobs
            sas_token: Optional SAS token for authentication
        """
        try:
            self.account_url = account_url
            self.container_name = container
            self.sas_token = sas_token
            
            # Initialize blob service client
            self.blob_service_client = BlobServiceClient(
                account_url=account_url,
                credential=sas_token
            )
            
            # Get container client
            self.container_client = self.blob_service_client.get_container_client(
                container=container
            )
            
            logger.info(f"BlobStorageClient initialized for container: {container}")
            
        except Exception as e:
            logger.error(f"BlobStorageClient initialization error: {e}")
            raise
    
    async def upload_file(self, object_key: str, data: Union[bytes, str],
                         mime: str = 'application/octet-stream',
                         overwrite: bool = True) -> Dict[str, Any]:
        """
        Upload file to Azure Blob Storage asynchronously.
        
        Args:
            object_key: Blob name/path (e.g., 'folder/file.txt')
            data: File content as bytes or string
            mime: MIME type for Content-Type header
            overwrite: Whether to overwrite existing blob
            
        Returns:
            Dictionary containing:
                - object_key: The blob name
                - url: Full URL to access the blob
                
        Raises:
            Exception: If upload fails
        """
        try:
            # Get blob client for this specific blob
            blob_client = self.container_client.get_blob_client(object_key)
            
            # Set content type
            content_settings = ContentSettings(content_type=mime)
            
            # Convert string to bytes if needed
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            # Upload blob
            await blob_client.upload_blob(
                data,
                overwrite=overwrite,
                content_settings=content_settings
            )
            
            # Construct URL
            url = blob_client.url
            if self.sas_token:
                url = f"{url}?{self.sas_token}"
            
            logger.info(f"Successfully uploaded blob: {object_key}")
            
            return {
                "object_key": object_key,
                "url": url
            }
            
        except Exception as e:
            logger.error(f"BlobStorageClient upload_file error: {e}")
            return {}
    
    async def download_file(self, object_key: str) -> Optional[bytes]:
        """Download file from blob storage."""
        try:
            blob_client = self.container_client.get_blob_client(object_key)
            downloader = await blob_client.download_blob()
            data = await downloader.readall()
            logger.info(f"Successfully downloaded blob: {object_key}")
            return data
        except Exception as e:
            logger.error(f"Download error: {e}")
            return None
    
    async def delete_file(self, object_key: str) -> bool:
        """Delete file from blob storage."""
        try:
            blob_client = self.container_client.get_blob_client(object_key)
            await blob_client.delete_blob()
            logger.info(f"Successfully deleted blob: {object_key}")
            return True
        except Exception as e:
            logger.error(f"Delete error: {e}")
            return False
    
    def list_blobs(self, prefix: Optional[str] = None):
        """List blobs in container."""
        try:
            blobs = self.container_client.list_blobs(name_starts_with=prefix)
            return [blob.name for blob in blobs]
        except Exception as e:
            logger.error(f"List blobs error: {e}")
            return []
```

## Technical Environment
- **Language**: Python 3.8+
- **Cloud Platform**: Microsoft Azure
- **SDK**: azure-storage-blob
- **Async Framework**: asyncio
- **Authentication**: SAS tokens

## Skills & Technologies
- **Azure Cloud Services**: Blob Storage, Storage Accounts
- **Python Async**: async/await, asyncio library
- **Azure SDK**: Python SDK for Azure services
- **REST APIs**: Understanding of cloud storage APIs
- **Authentication**: SAS tokens, connection strings
- **Error Handling**: Robust exception handling
- **Logging**: Structured logging for debugging

## Azure Blob Storage Concepts

### Storage Hierarchy
```
Storage Account
└── Container (like S3 bucket)
    └── Blob (file/object)
        ├── Block Blob (general files)
        ├── Page Blob (VHD files)
        └── Append Blob (logs)
```

### Authentication Methods
1. **Storage Account Keys**: Full access (not used here for security)
2. **SAS Tokens**: Time-limited, permission-scoped (used)
3. **Azure AD**: Identity-based authentication
4. **Anonymous**: Public read access

### Blob Types
- **Block Blobs**: General purpose (images, documents, videos)
- **Append Blobs**: Optimized for append operations (logs)
- **Page Blobs**: Random read/write (VHDs, databases)

## Use Cases

### Web Applications
- User-uploaded content (images, documents)
- Static website hosting
- Content delivery (with CDN)

### Data Storage
- Backup and disaster recovery
- Archive and long-term storage
- Data lakes and analytics

### Media Services
- Video streaming
- Image galleries
- Audio file storage

### Enterprise
- Document management systems
- Log aggregation
- Application data storage

## MIME Types
Common MIME types for content:
```python
MIME_TYPES = {
    # Images
    '.jpg': 'image/jpeg',
    '.png': 'image/png',
    '.gif': 'image/gif',
    '.svg': 'image/svg+xml',
    
    # Documents
    '.pdf': 'application/pdf',
    '.doc': 'application/msword',
    '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    
    # Text
    '.txt': 'text/plain',
    '.html': 'text/html',
    '.css': 'text/css',
    '.js': 'application/javascript',
    
    # Video
    '.mp4': 'video/mp4',
    '.webm': 'video/webm',
    
    # Audio
    '.mp3': 'audio/mpeg',
    '.wav': 'audio/wav',
}
```

## Example Usage

### Basic Upload
```python
import asyncio

async def main():
    # Initialize client
    client = BlobStorageClient(
        account_url="https://myaccount.blob.core.windows.net",
        container="uploads",
        sas_token="sv=2021-06-08&ss=b&srt=sco&sp=rwdlac&se=..."
    )
    
    # Upload text file
    result = await client.upload_file(
        object_key="documents/report.txt",
        data="Hello, Azure!",
        mime="text/plain"
    )
    
    print(f"Uploaded to: {result['url']}")

asyncio.run(main())
```

### Image Upload
```python
async def upload_image(image_path: str):
    client = BlobStorageClient(...)
    
    # Read image file
    with open(image_path, 'rb') as f:
        image_data = f.read()
    
    # Upload with correct MIME type
    result = await client.upload_file(
        object_key=f"images/{os.path.basename(image_path)}",
        data=image_data,
        mime="image/jpeg"
    )
    
    return result['url']
```

### Batch Upload
```python
async def batch_upload(files: list):
    client = BlobStorageClient(...)
    
    # Upload multiple files concurrently
    tasks = [
        client.upload_file(name, data, mime)
        for name, data, mime in files
    ]
    
    results = await asyncio.gather(*tasks)
    return results
```

## Error Handling

### Common Errors
1. **BlobAlreadyExists**: Blob exists and overwrite=False
2. **ContainerNotFound**: Container doesn't exist
3. **AuthenticationFailed**: Invalid SAS token
4. **ResourceNotFound**: Blob doesn't exist
5. **InvalidBlobOrBlock**: Malformed request

### Retry Strategy
```python
from azure.core.exceptions import AzureError
import asyncio

async def upload_with_retry(client, key, data, retries=3):
    for attempt in range(retries):
        try:
            return await client.upload_file(key, data)
        except AzureError as e:
            if attempt == retries - 1:
                raise
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
```

## Performance Optimization

### Concurrent Uploads
```python
# Upload multiple files in parallel
async def parallel_upload(files):
    client = BlobStorageClient(...)
    tasks = [client.upload_file(key, data) for key, data in files]
    return await asyncio.gather(*tasks)
```

### Chunked Upload (Large Files)
```python
# For files > 256MB, use chunked upload
async def upload_large_file(file_path, blob_name):
    blob_client = container_client.get_blob_client(blob_name)
    
    with open(file_path, 'rb') as f:
        await blob_client.upload_blob(
            f,
            overwrite=True,
            max_concurrency=4  # Parallel chunk uploads
        )
```

## Security Best Practices

### 1. SAS Token Management
- Set expiration times
- Limit permissions (read, write, delete)
- Use account-level or container-level SAS
- Rotate tokens regularly

### 2. Environment Variables
```python
import os

account_url = os.getenv('AZURE_STORAGE_ACCOUNT_URL')
sas_token = os.getenv('AZURE_STORAGE_SAS_TOKEN')
```

### 3. Validate Input
```python
def validate_blob_name(name: str) -> bool:
    # Check for path traversal
    if '..' in name:
        return False
    # Limit characters
    if not re.match(r'^[a-zA-Z0-9/_.-]+$', name):
        return False
    return True
```

## Learning Outcomes
This project demonstrates:
- Cloud storage integration with Azure
- Asynchronous Python programming
- Azure SDK usage
- Error handling in cloud applications
- Authentication with SAS tokens
- MIME type handling

## Real-World Applications
- **Content Management Systems**: User uploads
- **E-commerce**: Product images
- **SaaS Applications**: User files and documents
- **Mobile Apps**: Media storage backend
- **Data Pipelines**: Intermediate storage
- **Backup Systems**: Automated backups

## Cost Optimization
- Use appropriate storage tier (Hot, Cool, Archive)
- Implement lifecycle policies
- Compress data before upload
- Use CDN for frequently accessed content
- Monitor and analyze usage patterns

## Integration with Other Azure Services
- **Azure CDN**: Content delivery
- **Azure Functions**: Serverless processing
- **Azure Logic Apps**: Workflow automation
- **Azure Event Grid**: Event-driven architecture
- **Azure Cognitive Services**: AI processing

