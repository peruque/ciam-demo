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
   "code": code,
   "redirect_uri": COGNITO_REDIRECT_URI,
}
```

Good example: https://github.com/robotlearner001/blog/blob/main/fastapi-with-aws-cognito/main.py

## EC2 Instance Setup

- Configuration of Example

  - Name
    - Specify this in the tags:
    ```
      tags = {
         Name = "nano-instance"
      }
    ```
  - AMI image
    - ami-079db87dc4c10ac91
      - "Amazon Linux 2023 AMI 2023.3.20231218.0 x86_64 HVM kernel-6.1"
      - free tier
  - Key Pair (Login)
    - You can use a key pair to securely connect to your instance via ssh
    - Create a new key pair
      - Name: EC2 Tutorial 2
      - Key pair type: RSA
      - private key file format: .pem
        - .ppk is for Windows 8 and earlier so don't use this pretty much ever
  - Network Settings
    - Enable auto-assign public IP
    - Security Group
      - Like a Firewall to limit IP and ports
      - Allow SSH traffic from an IP
      - For this example allow HTTP traffic from internet
        - Should enable HTTPs for actual use
        - Since only HTTP is allowed, you need to use http in the browser to send request to instance
  - Storage
    - specify the EBS general purpose SSD
    - 1 Volume of 8 GiB (gp3) should be free
  - Advanced Details
    - Specify boot script in the user data section
  - Total Cost

    - EBS Storage: $0.08 x 8 GiB = $0.64 per month
    - t2.micro: $0.0116 x 730 hours = $8.47 per month
    - t2.nano: $0.0058 x 730 hours = $4.23 per month

      - This may not have enough memory

    - Other fees apply for data transfer

### ssh into instance

You will need to the .pem file that is associated to your EC2 instance.

1. Ensure that security group allows port 22 and your IP address (allow all IP addresses)
2. Change access for .pem file. Navigate to the location of the .pem file. Enter command:

```
chmod 0400 my-pem-file.pem
```

3. Run ssh command to login. You need to use the public IP address of the EC2 instance.

```
ssh -i my-pem-file.pem.pem ec2-user@123.456.789.10
```

4. logout by entering:

```
logout
```

### Provide EC2 Instance with a Role

- Associating a role to the instance will allow the instance to use AWS resources
