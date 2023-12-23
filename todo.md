## Fast API MVP of CIAM Demo

- [x] Use Settings for env vars instead of dot_env
- [x] Store access token in HttpOnly Cookie
  - delete when logging out
- [x] Use access token in header
- [x] Fix logging out so that token is no longer valid (or figure out what is the OAuth spec on logging out)
  - The access token is still valid. Need to delete the token from the cookies
- [x] Organize Endpoints and Enhance HTML
  - [x] Login Page to login
  - [x] Home Page to logout
  - [x] Two main content pages that require a token
  - [x] Add CSS
- [ ] Don't hardcode the logout redirect url
- [ ] Extract given and family name for the user and display on profile page
  - Need to change scope to just "openid"
  - Putting "openid" in the scope will return an id_token
  - attributes will be contained in the id_token not access_token
- [ ] Add tests to the repo
- [ ] Update Readme

## Create User Pool Using Terraform
