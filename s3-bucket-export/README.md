## s3 bucket export

This script will determine a buckets size, number of objects and the last modified date of the latest object (useful for seeing if a bucket is still being used)

The purpose of this script is to assist in assessing whether a bucket is still being used. Which will help determine if the bucket can be migrated to a cheaper storage class.

Note: This script makes a number of API calls which may incur a cost for buckets with many objects. At the time of writing it is $0.01 USD per 1,000 requests. The script will count how many API calls are made which is visible in the output file for reference. The API used in this script returns 1000 objects per call. So in theory a bucket would need to have at least (1000 * 1000 = 1,000,000) objects before you see any charges.