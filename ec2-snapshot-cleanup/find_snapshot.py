import boto3
from botocore.exceptions import ClientError
import csv
import os

region = "ap-southeast-2"

def read_ami_data(csv_file_path):
    """Read AMI data from the CSV file and return a list of dictionaries."""
    ami_data = []
    try:
        with open(csv_file_path, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                ami_data.append({
                    'ProfileName': row['Profile Name'],
                    'AMI Name': row['AMI Name'],
                    'AMI ID': row['AMI ID'],
                    'Creation Date': row['Creation Date']
                })
    except FileNotFoundError:
        print(f"File {csv_file_path} not found.")
    except KeyError as e:
        print(f"Missing expected column in {csv_file_path}: {e}")
    return ami_data

def find_snapshots_for_ami(profile, ami_id):
    """Find snapshots associated with the specified AMI in the given profile."""
    session = boto3.Session(profile_name=profile)
    ec2 = session.client('ec2', region_name=region)
    
    try:
        response = ec2.describe_images(ImageIds=[ami_id])
        block_device_mappings = response['Images'][0]['BlockDeviceMappings']
        
        snapshot_ids = [
            device['Ebs']['SnapshotId']
            for device in block_device_mappings
            if 'Ebs' in device and 'SnapshotId' in device['Ebs']
        ]
        
        if not snapshot_ids:
            return []  
        
        snapshots_response = ec2.describe_snapshots(SnapshotIds=snapshot_ids)
        
        snapshot_details = [
            {
                'ProfileName': profile,
                'AMI ID': ami_id,
                'SnapshotId': snapshot['SnapshotId'],
                'Description': snapshot.get('Description', 'N/A'),
                'CreationDate': snapshot['StartTime'].strftime('%Y-%m-%d')
            }
            for snapshot in snapshots_response['Snapshots']
        ]
        
        return snapshot_details
    
    except ClientError as e:
        print(f"Error accessing EC2 service for profile '{profile}': {e}")
        return []

def write_snapshots_to_csv(file_path, data):
    """Write snapshot data to a CSV file."""
    file_exists = os.path.isfile(file_path)
    
    with open(file_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        
        if not file_exists:
            writer.writerow(['Profile Name', 'AMI ID', 'Snapshot ID', 'Description', 'Creation Date'])
        
        for item in data:
            writer.writerow([item['ProfileName'], item['AMI ID'], item['SnapshotId'], item['Description'], item['CreationDate']])

if __name__ == "__main__":
    input_csv_file = "output/AMI.csv"
    output_csv_file = "output/Snapshots_for_AMI.csv"
    
    ami_data = read_ami_data(input_csv_file)
    all_snapshots = []

    for entry in ami_data:
        profile = entry['ProfileName']
        ami_id = entry['AMI ID']
        
        snapshots = find_snapshots_for_ami(profile, ami_id)
        all_snapshots.extend(snapshots)
        
        if snapshots:
            for snapshot in snapshots:
                print(f"Profile: {snapshot['ProfileName']}, AMI ID: {snapshot['AMI ID']}, Snapshot ID: {snapshot['SnapshotId']}, Description: {snapshot['Description']}, Creation Date: {snapshot['CreationDate']}")
        else:
            print(f"No snapshots found for AMI ID {ami_id} in profile: {profile}")

    if all_snapshots:
        write_snapshots_to_csv(output_csv_file, all_snapshots)
        print(f"Snapshot details have been written to {output_csv_file}")
    else:
        print("No snapshots found across all profiles.")
