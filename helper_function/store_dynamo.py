import boto3
from datetime import datetime
import os

def store_session_in_dynamodb(
    session_id, user_profile, s3_url
):
    dynamodb = boto3.resource("dynamodb",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_DEFAULT_REGION")
    )
    table = dynamodb.Table("medibuddyAI")
    item = {
        "SessionID": session_id,
        "CreatedAt": datetime.utcnow().isoformat(),
        "UserProfile": user_profile,
        "PDFLink": s3_url,
    }
    table.put_item(Item=item)
    return item
