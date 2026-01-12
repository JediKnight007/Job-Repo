from datetime import datetime, timedelta
from venv import logger
from azure.storage.blob import BlobServiceClient, generate_account_sas, ResourceTypes, AccountSasPermissions
from azure.storage.blob import ContainerClient, ContentSettings
from azure.storage.blob.aio import BlobClient
from typing import TYPE_CHECKING, Optional, Dict, Union, Any

class BlobStorageClient():

    def __init__(self, account_url: str, container: str, sas_token: Optional[str] = None):
        try:
            self.blob_client = BlobServiceClient(account_url=account_url, credential=credential)
            self.container_client: ContainerClient = self.data_lake_client.get_file_system_client(file_system=container)
            self.sas_token = sas_token
            logger.info("BlobStorageClient initialized")
        except Exception as e:
            logger.warn(f"BlobStorageClient initialization error: {e}")


    async def upload_file(self, object_key: str, data: Union[bytes, str], mime: str = 'application/octet-stream', overwrite: bool = True) -> Dict[str, Any]:
        try:
            file_client: BlobClient = self.container_client.get_blob_client(object_key)
            content_settings = ContentSettings(content_type=mime)
            file_client.upload_blob(data, overwrite=overwrite, content_settings=content_settings)
            url = f"{file_client.url}{self.sas_token}" if self.sas_token else file_client.url
            blob = BlobClient.from_connection_string(conn_str="<connection_string>", container_name="mycontainer", blob_name="my_blob")
            return {"object_key": object_key, "url": url}
        except Exception as e:
            logger.warn(f"AzureStorageClient, upload_file error: {e}")
            return {}
        
