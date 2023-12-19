provider "aws" {
  region  = var.aws_region
  profile = var.aws_profile
}

terraform {
  backend "s3" {} # Set via terraform init -backend-config=backend.conf
}

resource "aws_s3_bucket" "name" {
  bucket = "peruque-temp-bucket-1"
}

resource "aws_cognito_user_pool" "pool" {
  name = "ciam-demo"

  alias_attributes = [
    "email",
    "preferred_username"
  ]

  password_policy {
    minimum_length = 8
  }

  mfa_configuration = "OFF"

  admin_create_user_config {
    allow_admin_create_user_only = true
  }

  account_recovery_setting {
    recovery_mechanism {
      name     = "verified_email"
      priority = 1
    }
  }


}
