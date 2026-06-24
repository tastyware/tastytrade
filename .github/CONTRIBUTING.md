# Contributions
If you want to run tests locally before opening a PR you can do the following:
1. Export your OAuth secret, refresh token, and account number to the following environment variables: `TT_SECRET`, `TT_REFRESH`, and `TT_ACCOUNT`. The account should be a margin account.
2. Make sure you have at least one share of long $F in your account, which will be used to place the OCO complex order (nothing will fill), as well as at least $2 of buying power.
3. Run `make install` to create the virtual environment, `make lint` to test code formatting, and `make test` to run the tests locally.
