provider "aws" {
  region  = var.aws_region
  profile = var.aws_profile
}

terraform {
  backend "s3" {} # Set via terraform init -backend-config=backend.conf
}

module "ciam_demo_api" {
  source = "./modules/ciam_demo_api"
}
