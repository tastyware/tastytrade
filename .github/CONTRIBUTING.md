# Contributions

Since Tastytrade certification sessions are severely limited in capabilities, the test suite for this SDK requires the usage of your own Tastytrade credentials. In order to run the tests, you'll need to set up your Tastytrade credentials as repository secrets on your local fork.

Secrets are protected by Github and are not visible to anyone. You can read more about repository secrets [here](https://docs.github.com/en/actions/reference/encrypted-secrets).

## Steps to follow to contribute

1. Fork the repository to your personal Github account, NOT to an organization where others may be able to indirectly access your secrets.
2. Make your changes on the forked repository.
3. Navigate to the forked repository's settings page and click on "Secrets and variables" > "Actions".
4. Click on "New repository secret" to add your Tastytrade username named `TT_USERNAME`.
5. Finally, do the same with your password, naming it `TT_PASSWORD`.
