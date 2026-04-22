import streamlit as st
import pandas as pd
import time
import random

st.set_page_config(page_title="오픈소스SW기초 팀 배정", layout="wide")

# CSS 스타일: 리스트용 카드와 팀 발표용 카드 디자인
st.markdown("""
    <style>
    /* 공통 카드 스타일 */
    .student-card {
        background-color: #ffffff; border-radius: 8px; padding: 10px;
        margin-bottom: 8px; border: 1px solid #e1e4e8;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05); text-align: center;
    }
    .team-card {
        background-color: #ffffff; border-radius: 12px; padding: 20px;
        margin-bottom: 20px; border: 1px solid #e1e4e8;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }
    .team-title { color: #1f77b4; font-size: 1.4em; font-weight: bold; border-bottom: 2px solid #1f77b4; padding-bottom: 8px; margin-bottom: 15px; }
    .member-row { margin-bottom: 12px; padding: 10px; border-radius: 8px; min-height: 60px; display: flex; flex-direction: column; justify-content: center; }
    .g1-bg { background-color: #e8f4f8; border-left: 5px solid #1f77b4; }
    .member-name { font-size: 1.2em; font-weight: bold; color: #333; }
    .member-info { font-size: 0.85em; color: #666; }
    .badge { font-size: 0.7em; padding: 2px 6px; border-radius: 4px; margin-left: 5px; color: white; background-color: #1f77b4; }
    
    /* 애니메이션용 스타일 */
    .roulette-text { color: #ff4b4b; font-weight: bold; font-size: 1.1em; }
    </style>
    """, unsafe_allow_html=True)

def create_teams(df_clean):
    g1 = df_clean[df_clean['그룹'] == 1.0].sample(frac=1).to_dict('records')
    g2 = df_clean[df_clean['그룹'] == 2.0].sample(frac=1).to_dict('records')
    g3 = df_clean[df_clean['그룹'] == 3.0].sample(frac=1).to_dict('records')

    g1_3rd = [s for s in g1 if float(s['학년']) < 4]
    g1_4th = [s for s in g1 if float(s['학년']) >= 4]
    
    teams = []
    # G2 없는 2개 팀
    for _ in range(2):
        leader = g1_3rd.pop() if g1_3rd else g1_4th.pop()
        teams.append([leader, g3.pop(), g3.pop()])

    remaining_g1 = g1_3rd + g1_4th
    random.shuffle(remaining_g1)
    for _ in range(13):
        m1 = remaining_g1.pop() if remaining_g1 else None
        m2 = g2.pop() if g2 else None
        m3 = g3.pop() if g3 else None
        teams.append([m for m in [m1, m2, m3] if m])
    
    return teams

st.title("🎲 오픈소스 SW 기초 팀 배정 시스템")

uploaded_file = st.file_uploader("수정된 CSV 업로드", type=["csv"])

if uploaded_file:
    df_raw = pd.read_csv(uploaded_file, skiprows=7)
    df_clean = df_raw.iloc[:, [0, 2, 3, 4, 37]].dropna(subset=[df_raw.columns[0], df_raw.columns[37]])
    df_clean.columns = ['그룹', '학년', '학과', '학번', '성명']

    # 1. 그룹별 학생 리스트 (카드 구조, 스크롤 없음)
    st.subheader("👥 그룹별 참여 학생 현황")
    c1, c2, c3 = st.columns(3)
    
    for g_num, col in zip([1, 2, 3], [c1, c2, c3]):
        # 학년 -> 학번 -> 이름 순으로 정렬
        group_data = df_clean[df_clean['그룹'] == float(g_num)].sort_values(by=['학년', '학번', '성명'])
        col.markdown(f"### 그룹 {g_num} <small>({len(group_data)}명)</small>", unsafe_allow_html=True)
        
        for _, row in group_data.iterrows():
            sid = str(int(float(row['학번'])))
            col.markdown(f"""
                <div class="student-card">
                    <div style="font-size:0.8em; color:gray;">{int(row['학년'])}학년 | {sid}</div>
                    <div style="font-weight:bold; font-size:1.1em;">{row['성명']}</div>
                </div>
            """, unsafe_allow_html=True)

    st.divider()

    if st.button("🚀 팀 추첨 시작"):
        final_teams = create_teams(df_clean)
        st.subheader("🎊 최종 팀 배정 결과")
        
        # 3열 레이아웃 준비
        team_rows = [st.columns(3) for _ in range(5)]
        
        for idx, team_members in enumerate(final_teams):
            row_idx = idx // 3
            col_idx = idx % 3
            
            with team_rows[row_idx][col_idx]:
                # 팀 카드 틀 먼저 생성
                team_container = st.container()
                team_container.markdown(f'<div class="team-title">TEAM {idx + 1}</div>', unsafe_allow_html=True)
                
                # 멤버들을 한 명씩 룰렛 애니메이션으로 확정
                confirmed_members_html = ""
                
                # 팀 내부의 개별 멤버 컨테이너
                placeholders = [st.empty() for _ in range(len(team_members))]
                
                for m_idx, final_member in enumerate(team_members):
                    # 룰렛 효과
                    for _ in range(8): # 8번 회전
                        temp_member = df_clean.sample(1).iloc[0]
                        placeholders[m_idx].markdown(f"""
                            <div class="member-row" style="border: 1px dashed #ccc;">
                                <div class="roulette-text">🎲 추첨 중...</div>
                                <div style="color:#aaa;">{temp_member['성명']}</div>
                            </div>
                        """, unsafe_allow_html=True)
                        time.sleep(0.08)
                    
                    # 멤버 확정 데이터 생성
                    is_g1 = "g1-bg" if float(final_member['그룹']) == 1.0 else ""
                    badge = '<span class="badge">G1</span>' if float(final_member['그룹']) == 1.0 else ""
                    sid = str(int(float(final_member['학번'])))
                    grade = str(int(float(final_member['학년'])))
                    
                    member_html = f"""
                        <div class="member-row {is_g1}">
                            <div><span class="member-name">{final_member['성명']}</span>{badge}</div>
                            <div class="member-info">{grade}학년 | {sid} | {final_member['학과']}</div>
                        </div>
                    """
                    # 확정된 멤버 고정 출력
                    placeholders[m_idx].markdown(member_html, unsafe_allow_html=True)
                    time.sleep(0.3) # 다음 멤버 추첨 전 대기
                
                st.markdown("---") # 팀간 구분선
