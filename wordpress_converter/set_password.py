from wordpress_converter.models import Author

import getpass

from wordpress_converter import db

login = input("Enter author login: ")
user = Author.query.filter(Author.login==login).first()
if not user:
    print("That author does not exist")
else:
    password = getpass.getpass(prompt="Please enter your proposed password: ")
    password_check = getpass.getpass(prompt="Please repeat your proposed password: ")
    if password != password_check:
        print("Passwords do not match")
    else:
        user.save_password(password)
        db.session.add(user)
        db.session.commit()
        print("Password saved.")