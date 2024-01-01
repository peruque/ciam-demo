provider "aws" {
  region  = var.aws_region
  profile = var.aws_profile
}

terraform {
  backend "s3" {} # Set via terraform init -backend-config=backend.conf
}


module "user_directory" {
  source = "./modules/user_directory"

  user_pool_name = var.user_pool_name
  user_email     = var.example_user_email
}
