variable "aws_region" {
  type = string
}

variable "aws_profile" {
  type = string
}

variable "example_user_email" {
  type = string
}

variable "user_pool_name" {
  type    = string
  default = "ciam-demo-user-pool"
}
