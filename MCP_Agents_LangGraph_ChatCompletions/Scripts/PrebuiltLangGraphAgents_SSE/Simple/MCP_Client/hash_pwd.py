import streamlit_authenticator as stauth
#hashed_password = stauth.Hasher(['pwd_admin_stmcp']).generate()
hashed_password = stauth.Hasher.hash('pwd_admin_stmcp') #.hash_passwords('pwd_admin_stmcp')
print(hashed_password)