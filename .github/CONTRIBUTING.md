# Contributions

Since Tastytrade certification sessions are severely limited in capabilities, the test suite for this SDK requires the usage of your own Tastytrade credentials. In order to pass the tests, you'll need to set use your Tastytrade credentials to run the tests on your local fork

## Steps to follow to contribute

1. Fork the repository to your personal Github account and make your proposed changes.
2. Export your username, password, and account number to the following environment variables: `TT_USERNAME`, `TT_PASSWORD`, and `TT_ACCOUNT`.
3. Make sure you have at least one share of long $F in your account, which will be used to place the OCO complex order (nothing will fill).
4. Run `make venv` to create the virtual environment, then `make test` to run the tests locally.
