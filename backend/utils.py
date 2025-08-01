import boto3
from botocore.exceptions import NoCredentialsError
import os

# --- S3 Configuration ---
S3_BUCKET = os.getenv('S3_BUCKET_NAME')
S3_LOCATION = f'https://{S3_BUCKET}.s3.amazonaws.com/'
S3_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY_ID')
S3_SECRET_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
DEFAULT_PROFILE_PIC_URL = os.getenv('DEFAULT_PROFILE_PIC_URL')


def upload_to_s3(file, bucket_name, acl="public-read"):
    """
    Uploads a file object to an S3 bucket.
    """
    try:
        s3 = boto3.client(
           "s3",
           aws_access_key_id=S3_ACCESS_KEY,
           aws_secret_access_key=S3_SECRET_KEY
        )
        s3.upload_fileobj(
            file,
            bucket_name,
            file.filename,
            ExtraArgs={
                "ACL": acl,
                "ContentType": file.content_type
            }
        )
    except FileNotFoundError:
        print("The file was not found")
        return None
    except NoCredentialsError:
        print("Credentials not available")
        return None
    return f"{S3_LOCATION}{file.filename}"


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'avif'}

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}