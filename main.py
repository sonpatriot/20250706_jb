import streamlit as st
import pandas as pd
from auth_utils import authenticate_user

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    st.title("🔐 로그인")
    email = st.text_input("이메일")
    pw    = st.text_input("비밀번호", type="password")
    if st.button("로그인"):
        if authenticate_user(email, pw):
            st.session_state["logged_in"] = True
            st.session_state["user_email"] = email
            st.success("승인되었습니다. 로그인을 한번 더 클릭해주세요~")
        else:
            st.error("로그인 정보가 올바르지 않거나 승인되지 않은 계정입니다.")
    st.stop()

@st.cache_data
def load_data(file_path: str) -> pd.DataFrame:
    df = pd.read_excel(file_path)
    df.columns = df.columns.str.strip()
    return df


def analyze_applications(
    df: pd.DataFrame,
    college: str,
    major: str,
    sebyojeon: str,
    grade_min: float,
    grade_max: float
) -> pd.DataFrame:
    # 지원 대상 학생 추출
    cond = (
        (df['교과등급(기본)'] >= grade_min) &
        (df['교과등급(기본)'] <= grade_max) &
        (df['대학'] == college) &
        (df['모집단위'] == major) &
        (df['세부전형'] == sebyojeon)
    )
    target_ids = df.loc[cond, '고유번호'].unique()

    # 대상 학생들의 모든 지원 기록 가져오기
    subset = df[df['고유번호'].isin(target_ids)].copy()

    # 원본 조건 레코드 제외
    mask = (
        (subset['교과등급(기본)'] >= grade_min) &
        (subset['교과등급(기본)'] <= grade_max) &
        (subset['대학'] == college) &
        (subset['모집단위'] == major) &
        (subset['세부전형'] == sebyojeon)
    )
    subset = subset[~mask]

    # 연계 지원 현황 집계
    result = (
        subset
        .groupby(['대학', '모집단위', '세부전형', '최종'])
        .size()
        .reset_index(name='횟수')
        .sort_values(by='횟수', ascending=False)
    )
    return result


def main():
    # st.markdown('### 대학·모집단위·세부전형·교과등급 연계 지원 분석')

    # 사이드바: 파일 경로
    file_path = 'reshaped_2025_sample.xlsx' #샘플파일
    # file_path = 'reshaped_2025.xlsx' #원본파일
    df = load_data(file_path)

    # 교과등급 범위 입력
    st.sidebar.subheader('교과등급 범위 필터')
    grade_min = st.sidebar.number_input(
        '교과등급 최소값', 1.0, 9.0, 1.0, 0.01, format='%.2f'
    )
    grade_max = st.sidebar.number_input(
        '교과등급 최대값', 1.0, 9.0, 9.0, 0.01, format='%.2f'
    )

    # 대학·모집단위·세부전형 선택
    colleges = sorted(df['대학'].dropna().unique())
    selected_college = st.sidebar.selectbox('대학 선택', [''] + colleges)

    majors = []
    if selected_college:
        majors = sorted(
            df[df['대학'] == selected_college]['모집단위'].dropna().unique()
        )
    selected_major = st.sidebar.selectbox('모집단위 선택', [''] + majors)

    sebyojeons = []
    if selected_college and selected_major:
        sebyojeons = sorted(
            df[(df['대학'] == selected_college) & (df['모집단위'] == selected_major)]['세부전형'].dropna().unique()
        )
    selected_sebyojeon = st.sidebar.selectbox('세부전형 선택', [''] + sebyojeons)

    # 실행 및 결과 출력
    if selected_college and selected_major and selected_sebyojeon:
        st.markdown(
            f"#### 🎯교과등급 {grade_min:.2f}~{grade_max:.2f} \n "
            f"#### 🏛️{selected_college}/{selected_major}/{selected_sebyojeon} 지원자 연계 지원 현황"
        )

                # 사이드바 필터 요약 테이블
        cond = (
            (df['교과등급(기본)'] >= grade_min) &
            (df['교과등급(기본)'] <= grade_max) &
            (df['대학'] == selected_college) &
            (df['모집단위'] == selected_major) &
            (df['세부전형'] == selected_sebyojeon)
        )
        filtered = df[cond]
        status_counts = filtered['최종'].value_counts().reindex(['합', '충원합', '불'], fill_value=0)
        summary = pd.DataFrame({
            '총 지원횟수': [len(filtered)],
            '합': [status_counts['합']],
            '충원합': [status_counts['충원합']],
            '불': [status_counts['불']]
        })
                # 요약 테이블 컬럼명에 이모지 추가 및 색상 지정
        summary.columns = [
            '📊 총 지원횟수',
            '✅ 합',
            '🔄 충원합',
            '❌ 불'
        ]
        # HTML 테이블 렌더링으로 고정 너비 설정
        html = summary.to_html(index=False)
        # 기본 border 및 클래스 속성 제거
        html = html.replace('border="1"', '').replace('class="dataframe"', '')
        html = html.replace(
            '<table', '<table style="table-layout:fixed; width:100%;"'
        )
        # 각 헤더 셀 스타일: 너비, 정렬, 색상
        html = html.replace(
            '<th>', '<th style="width:25%; text-align:center; color:blue;">'
        )
        html = html.replace(
            '<td>', '<td style="overflow:hidden; text-align:center; text-overflow:ellipsis; white-space:nowrap;">'
        )
        st.markdown(html, unsafe_allow_html=True)
        st.markdown('#### \n')
        st.markdown('#### 🔍지원자의 타대학 지원 경향 및 결과')

        # 연계 지원 결과
        result_df = analyze_applications(
            df,
            selected_college,
            selected_major,
            selected_sebyojeon,
            grade_min,
            grade_max
        )
        if result_df.empty:
            st.write('연계 지원 데이터가 없습니다.')
        else:
            for status in ['합', '충원합', '불']:
                subset_status = result_df[result_df['최종'] == status]
                st.markdown(f"##### 🏫최종: {status}")
                if subset_status.empty:
                    st.write('데이터 없음')
                else:
                    display_df = subset_status[['대학', '모집단위', '세부전형', '횟수']].reset_index(drop=True)
                    st.table(display_df)
    else:
        st.write('사이드바에서 모든 필터를 설정해주세요.')

if __name__ == '__main__':
    main()