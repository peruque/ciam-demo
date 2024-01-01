
resource "aws_cognito_user_pool" "pool" {
  name = var.user_pool_name

  alias_attributes = [
    "email",
    "preferred_username"
  ]

  password_policy {
    minimum_length = 8
  }

  username_configuration {
    case_sensitive = false
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

  auto_verified_attributes = ["email"]

  user_attribute_update_settings {
    attributes_require_verification_before_update = ["email"]
  }

  schema {
    name                = "email"
    attribute_data_type = "String"
    required            = true
  }

  schema {
    name                = "given_name"
    attribute_data_type = "String"
    required            = true
    mutable             = true
  }

  schema {
    name                = "family_name"
    attribute_data_type = "String"
    required            = true
    mutable             = true
  }

}

resource "aws_cognito_user_pool_client" "client" {
  user_pool_id    = aws_cognito_user_pool.pool.id
  name            = "ciam-demo-client"
  generate_secret = true

  callback_urls = ["http://localhost:8000/callback"]
  logout_urls   = ["http://localhost:8000"]


  allowed_oauth_flows_user_pool_client = true
  supported_identity_providers         = ["COGNITO"]
  allowed_oauth_flows                  = ["code"]
  allowed_oauth_scopes                 = ["email", "openid"]
}

resource "aws_cognito_user_group" "basic" {
  user_pool_id = aws_cognito_user_pool.pool.id
  name         = "basic"
}

resource "aws_cognito_user_group" "green_team" {
  user_pool_id = aws_cognito_user_pool.pool.id
  name         = "green-team"
}

resource "aws_cognito_user_pool_domain" "pool" {
  user_pool_id = aws_cognito_user_pool.pool.id
  domain       = var.user_pool_name
}

resource "aws_cognito_user" "jndoe" {
  user_pool_id = aws_cognito_user_pool.pool.id
  username     = "jndoe"

  attributes = {
    given_name     = "John"
    family_name    = "Doe"
    email          = var.user_email
    email_verified = true
  }
}

resource "aws_cognito_user_in_group" "jndoe_basic" {
  user_pool_id = aws_cognito_user_pool.pool.id
  group_name   = aws_cognito_user_group.basic.name
  username     = aws_cognito_user.jndoe.username
}

resource "aws_cognito_user_in_group" "jndoe_green_team" {
  user_pool_id = aws_cognito_user_pool.pool.id
  group_name   = aws_cognito_user_group.green_team.name
  username     = aws_cognito_user.jndoe.username
}
