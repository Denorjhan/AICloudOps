import boto3

def create_alb():
    elbv2 = boto3.client('elbv2')
    alb_response = elbv2.create_load_balancer(
        Name='my-alb',
        Subnets=[
            'subnet-12345678',
            'subnet-87654321'
        ],
        SecurityGroups=['sg-abcdef01'],
        Scheme='internet-facing',
        Tags=[
            {
                'Key': 'Name',
                'Value': 'my-alb'
            }
        ]
    )
    print('ALB created:', alb_response)

create_alb()