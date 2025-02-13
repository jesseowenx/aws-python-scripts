import boto3
from botocore.exceptions import ClientError
import csv
import os

profiles = ["profile1", "profile2", "profile3"]
keyword = "deleteme" 
region = "ap-southeast-2"

def find_amis(profile, keyword):    
    session = boto3.Session(profile_name=profile)
    ec2 = session.client('ec2', region_name=region)
    response = ec2.describe_images(Owners=['self', 'amazon', 'aws-marketplace'])
    
    amis_with_keyword = [
        {
            'ProfileName': profile,
            'ImageId': image['ImageId'],
            'Name': image['Name'],
            'CreationDate': image['CreationDate']
        }
        for image in response['Images']
        if keyword in image['Name']
    ]
    
    return amis_with_keyword

def write_to_csv(file_path, data):
    file_exists = os.path.isfile(file_path)
    
    with open(file_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        
        if not file_exists:
            writer.writerow(['Profile Name', 'AMI Name', 'AMI ID', 'Creation Date'])
        
        for item in data:
            creation_date = item['CreationDate'].split('T')[0]
            writer.writerow([item['ProfileName'], item['Name'], item['ImageId'], creation_date])

if __name__ == "__main__":
    all_amis = []

    for profile in profiles:
        amis = find_amis(profile, keyword)
        all_amis.extend(amis)
        
        if amis:
            for ami in amis:
                print(f"Profile: {ami['ProfileName']}, AMI ID: {ami['ImageId']}, Name: {ami['Name']}, Creation Date: {ami['CreationDate']}")
        else:
            print(f"No AMIs found with the specified keyword for profile: {profile}")
            
    directory = 'output'
    os.makedirs(directory, exist_ok=True)
    csv_file_path = os.path.join(directory, 'AMI.csv')
    write_to_csv(csv_file_path, all_amis)
 