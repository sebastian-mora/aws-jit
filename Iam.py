
import boto3
import json

iam = boto3.client('iam')


def append_trust_policy(role_name, arn):
  response = iam.get_role(RoleName=role_name)
  trust_policy = response['Role']['AssumeRolePolicyDocument']

  print(trust_policy)

  # change principle to '123456'
  trust_policy['Statement'][0]['Principal']['AWS'].append(arn)

  print(trust_policy['Statement'][0]['Principal']['AWS'])

  res = iam.update_assume_role_policy(RoleName=role_name, PolicyDocument=json.dumps(trust_policy))
  print(res)

def remove_role_trust_policy(role_name, arn):
  response = iam.get_role(RoleName=role_name)
  trust_policy = response['Role']['AssumeRolePolicyDocument']

  print(trust_policy)

  # change principle to '123456'
  trust_policy['Statement'][0]['Principal']['AWS'].remove(arn)

  print(trust_policy['Statement'][0]['Principal']['AWS'])

  res = iam.update_assume_role_policy(RoleName=role_name, PolicyDocument=json.dumps(trust_policy))
  print(res)


def lambda_handler(event, context):

    requestor_arn = event.get('requestor_arn')

    response = {'result': requestor_arn}
    return response