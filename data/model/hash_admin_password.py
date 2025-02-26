from passlib.context import CryptContext

# Setup password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Replace 'your_admin_password' with the actual admin password you want to hash
admin_password = "gaurav123456"

# Generate the hashed password
hashed_password = pwd_context.hash(admin_password)

print("Hashed Admin Password:", hashed_password)
