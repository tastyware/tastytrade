from tastytrade import Session


def test_get_customer(session):
    assert session.get_customer() != {}


def test_destroy(get_cert_credentials):
    usr, pwd = get_cert_credentials
    session = Session(usr, pwd, is_test=True)
    session.destroy()
