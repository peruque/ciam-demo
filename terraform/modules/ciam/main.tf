
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
