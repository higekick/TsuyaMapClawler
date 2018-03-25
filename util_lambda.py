import boto3

s3 = boto3.resource('s3')
bucket = s3.Bucket('tsuyama-open')

def delDirInBucket():
    delFileInBucket('csv/')
    delFileInBucket('jpg/')

def delFileInBucket(dir):
    for obj in bucket.objects.filter(Prefix=dir):
        s3.Object(bucket.name, obj.key).delete()

def uploadToBucket(filePath, prefix):
    tmp = filePath.split('/')
    fileName = tmp[-1]
    upPath = prefix + '/' + fileName
    bucket.upload_file(filePath, upPath)
