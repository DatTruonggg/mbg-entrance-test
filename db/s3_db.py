import boto3
import json
from datetime import datetime
from typing import Dict, Any
from configs import config
from botocore.exceptions import BotoCoreError, NoCredentialsError

class S3Handler:
    def __init__(self):

        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=config.aws_access_key_id,
            aws_secret_access_key=config.aws_secret_access_key,
            region_name=config.region
        )
        self.bucket_name = config.bucket.replace("s3://", "")

    def upload_report(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Lưu báo cáo lên S3, sử dụng `user_id` thay vì `report_id`.
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            folder_date = datetime.now().strftime("%Y/%m/%d") 

            user_id = report_data.get("user_id", "unknown_user")

            query_slug = "".join(c if c.isalnum() else "_" for c in report_data.get("query", "unknown")[:30])

            file_path = f"reports/{folder_date}/{user_id}_{timestamp}_{query_slug}.json"

            report_json = json.dumps(report_data, indent=2)
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_path,
                Body=report_json.encode('utf-8'),
                ContentType='application/json'
            )

            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': file_path},
                ExpiresIn=86400
            )

            return {
                "success": True,
                "user_id": user_id,
                "file_path": file_path,
                "url": url,
                "timestamp": timestamp
            }

        except (BotoCoreError, NoCredentialsError) as e:
            print(f"AWS S3 Error: {e}")
            return {"success": False, "error": str(e)}

    def get_recent_reports(self, limit: int = 10) -> Dict[str, Any]:

        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix="reports/",
                MaxKeys=limit
            )

            reports = []
            if "Contents" in response:
                for item in sorted(response["Contents"], key=lambda x: x["LastModified"], reverse=True)[:limit]:
                    url = self.s3_client.generate_presigned_url(
                        'get_object',
                        Params={'Bucket': self.bucket_name, 'Key': item["Key"]},
                        ExpiresIn=3600
                    )

                    reports.append({
                        "file_path": item["Key"],
                        "last_modified": item["LastModified"].isoformat(),
                        "size": item["Size"],
                        "url": url
                    })

            return {
                "success": True,
                "reports": reports
            }

        except (BotoCoreError, NoCredentialsError) as e:
            print(f"AWS S3 Error: {e}")
            return {"success": False, "error": str(e), "reports": []}
