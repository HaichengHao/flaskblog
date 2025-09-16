from werkzeug.security import generate_password_hash, check_password_hash

password = "nikofox"
hashed = "pbkdf2:sha256:600000$GUwlh2SxpW5vQdIg$58bcef279577e34b9f23741db1d1b07822e644e06bf168c714fc73cff2b88cd7"

print(check_password_hash(hashed, password))
# 输出应该是 False