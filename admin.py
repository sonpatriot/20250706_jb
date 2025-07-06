# admin.py
import streamlit as st
from auth_utils import create_user_table, get_pending_users, approve_user

def main():
    create_user_table()
    st.title("🔑 관리자 승인(Admin) 페이지")
    pwd = st.text_input("관리자 비밀번호 입력", type="password")
    if pwd != st.secrets["admin"]["admin_password"]:
        st.stop()
    pending = get_pending_users()
    if not pending:
        st.info("승인 대기중인 사용자가 없습니다.")
    for user in pending:
        cols = st.columns([3,1])
        cols[0].write(f"{user['username']} ({user['email']})")
        if cols[1].button("승인", key=user['email']):
            st.success("승인되었습니다! 페이지를 새로고침해주세요.")
            st.stop()
if __name__ == "__main__":
    main()
