import boto3
from botocore.exceptions import ClientError
import csv
import os 

profile = "profile_name"
session = boto3.Session(profile_name=profile)
s3 = session.client('s3')

directory = 'output'
os.makedirs(directory, exist_ok=True)
csv_file_path = os.path.join(directory, profile + '_s3_metadata.csv')
csv_file = open(csv_file_path, 'w', newline='', encoding='utf-8')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(['Bucket','Bucket Size (MB)', 'Most Recent Object Key', 'Last Modified', 'Total Objects', 'API Call Count'])

buckets_resp = s3.list_buckets()

for bucket in buckets_resp["Buckets"]:
    bucket_name = bucket["Name"]
    print(f"Bucket: {bucket_name}")

    total_size = 0
    total_objects = 0
    most_recent_object = None
    latest_date = None
    api_call_count = 0

    paginator = s3.get_paginator('list_objects_v2')

    try:
        for page in paginator.paginate(Bucket=bucket_name):
            api_call_count += 1
            if "Contents" in page:
                for obj in page["Contents"]:
                    total_size += obj["Size"]
                    total_objects += 1
                    last_modified = obj["LastModified"]
                    if latest_date is None or last_modified > latest_date:
                        latest_date = last_modified
                        most_recent_object = obj
                    last_modified_str = last_modified.strftime('%Y-%m-%d %H:%M:%S')
                    print(f"Object: {obj['Key']}, Last Modified: {last_modified_str}")

        if most_recent_object:
            csv_writer.writerow([bucket_name,f"{total_size / (1024 * 1024):.2f}", most_recent_object['Key'], latest_date.strftime('%Y-%m-%d %H:%M:%S'), total_objects, api_call_count])

    except ClientError as e:
        if e.response['Error']['Code'] == 'AccessDenied':
            print(f"Access denied for bucket {bucket_name}. Skipping...")
            csv_writer.writerow([bucket_name, 'AccessDenied','AccessDenied','AccessDenied','AccessDenied','AccessDenied'])
            continue
        else:
            print(f"Error processing bucket {bucket_name}: {e}")
            csv_writer.writerow([bucket_name, e, e, e, e, e])
            continue  

    if latest_date:
        print(f"Most recent write time in {bucket_name}: {latest_date.strftime('%Y-%m-%d %H:%M:%S')}")

    print(f"Total Size: {total_size / (1024*1024):.2f} MB")
    print(f"Total Objects: {total_objects}")
    print() 

csv_file.close()
