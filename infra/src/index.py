
import boto3
import json
from os import getenv

iam = boto3.client('iam')

ADMIN_ROLE_NAME = getenv("ADMIN_ROLE_NAME")

def append_trust_policy(role_name, arn):
  response = iam.get_role(RoleName=role_name)
  trust_policy = response['Role']['AssumeRolePolicyDocument']

  # change principle to '123456'
  if isinstance(trust_policy['Statement'][0]['Principal']['AWS'], str):
    trust_policy['Statement'][0]['Principal']['AWS'] = [trust_policy['Statement'][0]['Principal']['AWS'], arn]
  else:
    trust_policy['Statement'][0]['Principal']['AWS'].append(arn)

  res = iam.update_assume_role_policy(RoleName=role_name, PolicyDocument=json.dumps(trust_policy))

def remove_role_trust_policy(role_name, arn):
  response = iam.get_role(RoleName=role_name)
  trust_policy = response['Role']['AssumeRolePolicyDocument']


  # change principle to '123456'
  trust_policy['Statement'][0]['Principal']['AWS'].remove(arn)
  res = iam.update_assume_role_policy(RoleName=role_name, PolicyDocument=json.dumps(trust_policy))


def lambda_handler(event, context):

    requester_arn = event.get('requester_arn')
    action = event.get('action')
    approve_name = event.get('approver_name')
    
    if action == 'append':
      append_trust_policy(ADMIN_ROLE_NAME, requester_arn)
  
    if action == 'remove':
      remove_role_trust_policy(ADMIN_ROLE_NAME, requester_arn)
      
    response = {'requester_arn': requester_arn, 'action': action, 'approver_name': approve_name}, 
    return response