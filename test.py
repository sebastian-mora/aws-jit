from time import sleep
import boto3
from botocore.exceptions import ClientError
from botocore.paginate import Paginator

ACCOUNT_ID='722461077209'
REQUESTOR_ARN="arn:aws:iam::722461077209:role/test-jit"
MaxSessionDuration='1' #hrs
ADMIN_POLICY_ARN='arn:aws:iam::aws:policy/AdministratorAccess'

iam_client = boto3.resource('iam')

def lambda_handler(event, context):
 

  role_iterator = iam_client.roles.filter(
  )

  print(role_iterator)

  while True:

    for role in role_iterator:
      print(role.tags)
  
    break

  print("done")


lambda_handler(1,1)