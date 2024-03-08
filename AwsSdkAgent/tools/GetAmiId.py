from agency_swarm.tools import BaseTool
from pydantic import Field
import subprocess
import ast
import sys
import boto3
from operator import itemgetter


class GetAmiId(BaseTool):
    """Returns a list of Amazon-Linux AMI IDs in the current region."""

    def run(self):
        """Executes a terminal command to get a list of available AMI IDs."""
        client = boto3.client('ec2')
        response = client.describe_images(
        Filters=[
            {
                'Name': 'description',
                'Values': [
                    'Amazon Linux AMI*',  # You can adjust this value to match the AMIs you're interested in
                ]
            },
        ],
        Owners=[
            'amazon'  # This is set to 'amazon' to get AMIs owned by Amazon. Adjust as needed.
        ]
    )

       # Sort on Creation date Desc
        image_details = sorted(response['Images'], key=itemgetter('CreationDate'), reverse=True)

        # Initialize an empty string to hold the AMI IDs
        ami_ids_str = ''
        
        # Loop through the sorted image details
        for image in image_details:
            ami_ids_str += image['ImageId'] + ' '  # Add each AMI ID to the string followed by a space

        return ami_ids_str.strip()  # Return the string of AMI IDs, .strip() removes any trailing space
