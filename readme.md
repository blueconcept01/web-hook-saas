## Installation
Install Docker: https://docs.docker.com/engine/install/

Make you are in the web-hook-saas folder then run: 
`docker build -t web-hook-service web-hook-service`

`docker run -d --name web-hook-service -p 80:80 web-hook-service`

## API requirements:

### post_web_hook - This will queue in a webhook job to be run until the response returns 200 or the retries are used up with exponential backup.

REQUIRED PARAMETERS:

`method` - Name of the request type like GET, POST, etc.
`url` - Name of the url to send the request to 

For example: `{'method': 'POST', 'url': 'https://www.google.com/'}`

OPTIONAL parameters:

`params` - params of the request
`data` - data of the request
`headers` - headers of the request

RETURNS:

`{'id': [HOOK_ID], 'request_payload': [WEBHOOK JOB CONFIGURATION]}`

### get_hook_status - Retrieves the webhook job configuration info including the status (sent, retrying, failed)

REQUIRED PARAMETERS:

`id` - Name of id of the webhook job 

For example: `{'id': 596b7684-3ea1-4fad-8d2a-f23f421d5005}`

RETURNS:

`{'id': [HOOK_ID], 'request_payload': [WEBHOOK JOB CONFIGURATION]}`