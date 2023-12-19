# Customer Identity Access Management Demonstration

## Running Locally

### Running Example

```
uvicorn api.example:app --reload
```

## Create AWS Cognito User Pool via Terraform

1. Create state bucket
2. Create file for backend configuration named: `backend.conf`

   ```conf
   bucket = "<state bucket name>"
   key = "<state file name>.tfstate"
   region = "<AWS region>"
   profile = "<AWS profile>"
   ```

3. Create file for terraform variables named: `terraform.tfvars`

   ```conf
   aws_region  = "<AWS region>"
   aws_profile = "<AWS profile>"
   ```

4. Initialize terraform:
   ```
   terraform init -backend-config=backend.conf
   ```

## Working with User Pool

### Cognito Host UI

```
https://<your_domain>/login?response_type=code&client_id=<your_app_client_id>&redirect_uri=<your_callback_url>
```

Note that the redirect URL must match one of the listed redirect URLs.

You can view the Hosted UI by going to Clients for the user pool.
