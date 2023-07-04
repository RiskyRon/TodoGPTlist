import boto3
import os
from dotenv import load_dotenv
import quart, json
from main import app
load_dotenv()

# gpt please check this S3 part for errors
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")



# Create an S3 client
s3 = boto3.client('s3',
                    aws_access_key_id=AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                    region_name=AWS_REGION)



@app.post("/s3/upload")
async def upload_file_to_s3():
    file = await request.files.get('file')
    if file:
        try:
            s3.upload_fileobj(file, file.filename)
            return quart.Response(response='File uploaded successfully', status=200)
        except Exception as e:
            return quart.Response(response=str(e), status=400)
    else:
        return quart.Response(response='No file provided', status=400)



@app.get("/s3/<filename>")
async def get_s3_file(filename):
    try:
        response = s3.get_object(Bucket=AWS_S3_BUCKET, Key=filename)
        file_content = response['Body'].read().decode('utf-8')
        return quart.Response(response=file_content, status=200)
    except Exception as e:
        return quart.Response(response=str(e), status=400)
    


@app.delete("/s3/<filename>")
async def delete_file_from_s3(filename):
    try:
        s3.delete_object(Bucket=AWS_S3_BUCKET, Key=filename)
        return quart.Response(response='File deleted successfully', status=200)
    except Exception as e:
        return quart.Response(response=str(e), status=400)



@app.get("/s3")
async def list_files_in_s3():
    try:
        response = s3.list_objects(Bucket=AWS_S3_BUCKET)
        files = [file['Key'] for file in response.get('Contents', [])]
        return quart.Response(response=json.dumps(files), status=200)
    except Exception as e:
        return quart.Response(response=str(e), status=400)


