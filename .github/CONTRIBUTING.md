# Contributions

Since Tastytrade certification sessions are severely limited in capabilities, the test suite for this SDK requires the usage of your own Tastytrade credentials. In order to pass the tests, you'll need to set use your Tastytrade credentials to run the tests on your local fork.

## Steps to follow to contribute

1. Fork the repository to your personal Github account and make your proposed changes.
2. Export your username, password, and account number to the following environment variables: `TT_USERNAME`, `TT_PASSWORD`, and `TT_ACCOUNT`. The account should be a margin account.
3. Make sure you have at least one share of long $F in your account, which will be used to place the OCO complex order (nothing will fill), as well as at least $2 of buying power.
4. Run `make install` to create the virtual environment, then `make lint` and `make test` to run the tests locally.
