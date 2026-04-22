import streamlit as st
import pandas as pd
import random

def create_complex_teams(df):
    # 1. 데이터 전처리
    # '학년(기)' 컬럼 인덱스가 파일마다 다를 수 있어 유동적으로 처리
    df = df.iloc[:, [0, 2, 3, 4, 37]].dropna(subset=[df.columns[0], df.columns[37]])
    df.columns = ['그룹', '학년', '학과', '학번', '성명']
    
    # 임성은 학생 그룹 3으로 변경 (사용자 요청)
    df.loc[df['성명'] == '임성은', '그룹'] = 3.0
    
    # 2. 그룹별 분리 및 셔플
    g1 = df[df['그룹'] == 1.0].sample(frac=1).to_dict('records')
    g2 = df[df['그룹'] == 2.0].sample(frac=1).to_dict('records')
    g3 = df[df['그룹'] == 3.0].sample(frac=1).to_dict('records')
    
    # 3. 그룹 1 내에서 학년별 분리 (G2 없는 팀에 4학년 제외 조건용)
    g1_3rd = [s for s in g1 if s['학년'] < 4]
    g1_4th = [s for s in g1 if s['학년'] >= 4]
    
    teams = []
    
    # [조건 1] 그룹 2가 포함되지 않는 2개 팀 선배정 
    # (그룹 1의 4학년 제외 -> 즉, 그룹 1의 3학년 배치)
    for _ in range(2):
        if g1_3rd:
            leader = g1_3rd.pop()
        else: # 혹시라도 3학년이 부족할 경우 대비 (데이터 안전장치)
            leader = g1_4th.pop()
            
        team = [leader, g3.pop(), g3.pop()]
        teams.append({"type": "G1(3rd)+G3+G3", "members": team})

    # [조건 2] 남은 13개 팀 배정 (G1 + G2 + G3)
    # 남은 G1 인원 합치기
    remaining_g1 = g1_3rd + g1_4th
    random.shuffle(remaining_g1)
    
    for _ in range(13):
        team = [remaining_g1.pop(), g2.pop(), g3.pop()]
        teams.append({"type": "G1+G2+G3", "members": team})

    # 4. 결과 데이터프레임 생성
    result_data = []
    for idx, t_obj in enumerate(teams):
        for member in t_obj['members']:
            result_data.append({
                "팀번호": f"{idx + 1}팀",
                "성명": member['성명'],
                "학년": int(member['학년']),
                "학번": int(member['학번']),
                "학과": member['학과'],
                "기존그룹": int(member['그룹']),
                "팀유형": t_obj['type']
            })
    
    return pd.DataFrame(result_data)

# --- Streamlit GUI 구성 ---
st.set_page_config(page_title="오픈소스SW기초 팀 빌딩", layout="wide")

st.title("🎓 맞춤형 랜덤 팀 빌딩 시스템")
st.sidebar.header("설정 및 규칙")
st.sidebar.info("""
**적용된 특수 규칙:**
1. **임성은 학생**: 그룹 3으로 자동 변경
2. **G1/G2 분리**: 그룹 1과 2는 절대 같은 팀 안됨
3. **G2 미포함 팀**: 그룹 1에서 4학년 배제
4. **구성**: 3인 1조, 총 15개 팀
""")

uploaded_file = st.file_uploader("학생 명단 CSV 파일을 업로드하세요 (OpenSWBasic_6.xls 형식)", type=["csv"])

if uploaded_file:
    # 데이터 로드 (헤더가 8번째 줄에 있음)
    df_raw = pd.read_csv(uploaded_file, skiprows=7)
    
    if st.button("🚀 팀 구성 시작"):
        try:
            result_df = create_complex_teams(df_raw)
            
            st.success("✅ 조건에 맞는 팀 구성이 완료되었습니다!")
            
            # 요약 통계
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("📊 팀별 명단")
                st.dataframe(result_df, height=500)
            
            with col2:
                st.subheader("🔍 조건 검증")
                g2_none_teams = result_df[result_df['팀유형'] == "G1(3rd)+G3+G3"]
                st.write("**그룹 2가 없는 팀의 G1 학년 확인 (모두 3 이여야 함):**")
                st.write(g2_none_teams[g2_none_teams['기존그룹'] == 1][['팀번호', '성명', '학년']])
                
                # 다운로드
                csv = result_df.to_csv(index=False).encode('utf-8-sig')
                st.download_button(
                    label="📥 팀 구성 결과 다운로드 (CSV)",
                    data=csv,
                    file_name='final_team_allocation.csv',
                    mime='text/csv',
                )
        except Exception as e:
            st.error(f"오류가 발생했습니다. 파일 형식을 확인해주세요: {e}")
