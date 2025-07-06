# signup.py
import streamlit as st
from auth_utils import create_user_table, add_user

def main():
    create_user_table()
    st.title("📝 회원가입 (Signup)")
    with st.form("signup"):
        email    = st.text_input("이메일 (Email)")
        username = st.text_input("사용자 이름 (Username)")
        password = st.text_input("비밀번호 (Password)", type="password")
        submitted = st.form_submit_button("가입 요청")
    if submitted:
        success = add_user(email, username, password)
        if success:
            st.success("가입 요청이 접수되었습니다. 관리자 승인을 기다려주세요.")
        else:
            st.error("이미 가입된 이메일입니다.")

if __name__ == "__main__":
    main()
