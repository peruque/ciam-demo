# Consumer Identity Access Management Demonstration

## Running Locally

### Initial Setup

Navigate to the root directory of the project. Run commands:

```
python -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
```

### Running Example

```
uvicorn app.main:app --reload
```

or run

```
python3 run.py
```

## Create AWS Cognito User Pool via Terraform

1. Create state bucket
2. Create state lock Dynamo DB Table

- Create via management console
- Specify the following
  - name
  - Partition key: `LockID` string
  - Capacity mode: "On Demand"

3. Create file for backend configuration named: `backend.conf`

   ```conf
   bucket = "<state bucket name>"
   key = "<state file name>.tfstate"
   region = "<AWS region>"
   profile = "<AWS profile>"
   dynamodb_table = "<Name of Dynamo DB table>"
   ```

4. Create file for terraform variables named: `terraform.tfvars`

   ```conf
   aws_region  = "<AWS region>"
   aws_profile = "<AWS profile>"
   ```

5. Initialize terraform:
   ```
   terraform init -backend-config=backend.conf
   ```

### Cognito Host UI

```
https://<your_domain>/login?response_type=code&client_id=<your_app_client_id>&redirect_uri=<your_callback_url>
```

Note that the redirect URL must match one of the listed redirect URLs.

You can view the Hosted UI by going to Clients for the user pool.

## OAuth 2.0 Authorization Code Flow for Web Apps

1. GET Request to Login Button

   - Usually returns web page with form to submit request to go to the Authorization Server Login Page

2. GET Request to Authorization Server

   - The web page form fills in:
     - response_type: "code"
     - client_id
     - redirect_uri

3. GET Request from Authorization Server back to App

   - contains code in the query parameters
     - code is temporary and one time use
   - Goes to the redirect_uri specified in previous request

4. POST Request from App to Authorization Server

```python
{
   "grant_type": "authorization_code",
   "client_id": COGNITO_CLIENT_ID,
   "client_secret": COGNITO_CLIENT_SECRET,
   "code": <authorization code>,
   "redirect_uri": COGNITO_REDIRECT_URI,
}
```

Good example: https://github.com/robotlearner001/blog/blob/main/fastapi-with-aws-cognito/main.py
