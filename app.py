import streamlit as st
import pandas as pd
import time
import random

st.set_page_config(page_title="오픈소스SW기초 팀 배정", layout="wide")

# CSS 스타일 정의
st.markdown("""
    <style>
    .group-container {
        background-color: #f1f3f5; border-radius: 15px; padding: 15px;
        margin-bottom: 20px; border: 2px solid #dee2e6; min-height: 400px;
    }
    .student-card {
        background-color: #ffffff; border-radius: 8px; padding: 8px;
        margin: 4px; border: 1px solid #e1e4e8;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05); display: inline-block;
        width: calc(50% - 12px); vertical-align: top; text-align: left;
    }
    .st-dept { font-size: 0.75em; color: #1f77b4; font-weight: bold; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .st-name { font-size: 1.0em; font-weight: bold; color: #333; margin: 2px 0; }
    .st-info { font-size: 0.7em; color: #777; }
    
    .team-card {
        background-color: #ffffff; border-radius: 12px; padding: 20px;
        margin-bottom: 20px; border: 1px solid #e1e4e8;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }
    .team-title { color: #1f77b4; font-size: 1.4em; font-weight: bold; border-bottom: 2px solid #1f77b4; padding-bottom: 8px; margin-bottom: 15px; }
    .member-row { margin-bottom: 12px; padding: 10px; border-radius: 8px; min-height: 65px; display: flex; flex-direction: column; justify-content: center; }
    .g1-bg { background-color: #e8f4f8; border-left: 5px solid #1f77b4; }
    .badge { font-size: 0.7em; padding: 2px 6px; border-radius: 4px; margin-left: 5px; color: white; background-color: #1f77b4; }
    .roulette-text { color: #ff4b4b; font-weight: bold; font-size: 0.9em; }
    </style>
    """, unsafe_allow_html=True)

def get_final_teams(df_clean):
    g1 = df_clean[df_clean['그룹'] == 1.0].sample(frac=1).to_dict('records')
    g2 = df_clean[df_clean['그룹'] == 2.0].sample(frac=1).to_dict('records')
    g3 = df_clean[df_clean['그룹'] == 3.0].sample(frac=1).to_dict('records')
    g1_3rd = [s for s in g1 if float(s['학년']) < 4]; g1_4th = [s for s in g1 if float(s['학년']) >= 4]
    
    teams = []
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

    # 1. 그룹별 참여 학생 현황
    st.subheader("👥 그룹별 참여 학생 현황")
    c1, c2, c3 = st.columns(3)
    
    for g_num, col in zip([1, 2, 3], [c1, c2, c3]):
        group_data = df_clean[df_clean['그룹'] == float(g_num)].sort_values(by=['학년', '학번', '성명'])
        inner_html = ""
        for _, row in group_data.iterrows():
            sid = str(int(float(row['학번'])))
            dept = row['학과'].replace("SW융합대학 ", "")
            inner_html += f"""
                <div class="student-card">
                    <div class="st-dept">{dept}</div>
                    <div class="st-name">{row['성명']}</div>
                    <div class="st-info">{int(row['학년'])}학년 | {sid}</div>
                </div>
            """
        with col:
            st.markdown(f"""
                <div class="group-container">
                    <h4 style="text-align:center; color:#495057; margin-bottom:15px;">Group {g_num} ({len(group_data)}명)</h4>
                    {inner_html}
                    <div style="clear:both;"></div>
                </div>
            """, unsafe_allow_html=True)

    st.divider()

    # 2. 팀 추첨 로직 (세션 상태 관리 개선)
    if 'current_team_idx' not in st.session_state:
        st.session_state.current_team_idx = 0
    if 'teams_list' not in st.session_state:
        st.session_state.teams_list = []

    c_btn1, c_btn2 = st.columns([1, 5])
    
    # [전체 팀 생성] 버튼
    if c_btn1.button("🔥 전체 팀 생성"):
        st.session_state.teams_list = get_final_teams(df_clean)
        st.session_state.current_team_idx = 0
        st.rerun()

    # [다음 팀 추첨] 버튼 (한 번만 눌러도 즉시 애니메이션 시작)
    if st.session_state.teams_list:
        if st.session_state.current_team_idx < 15:
            # 이 버튼을 누르면 인덱스가 즉시 증가하고 화면이 다시 그려집니다.
            if st.button(f"➡️ {st.session_state.current_team_idx + 1}팀 추첨하기"):
                st.session_state.current_team_idx += 1
                st.rerun()
        
        st.subheader(f"🎊 배정 결과 ({st.session_state.current_team_idx}/15)")
        t_cols = st.columns(3)
        
        for i in range(st.session_state.current_team_idx):
            with t_cols[i % 3]:
                team_members = st.session_state.teams_list[i]
                
                # 방금 버튼을 눌러서 추가된 가장 마지막 팀만 애니메이션 효과
                if i == st.session_state.current_team_idx - 1:
                    st.markdown(f'<div class="team-title">TEAM {i + 1}</div>', unsafe_allow_html=True)
                    placeholders = [st.empty() for _ in range(len(team_members))]
                    
                    for m_idx, final_member in enumerate(team_members):
                        # 룰렛 애니메이션
                        for _ in range(6):
                            temp = df_clean.sample(1).iloc[0]
                            placeholders[m_idx].markdown(f'<div class="member-row" style="border: 1px dashed #ccc;"><div class="roulette-text">🎲 추첨 중...</div><div style="color:#aaa;">{temp["성명"]}</div></div>', unsafe_allow_html=True)
                            time.sleep(0.05)
                        
                        # 실제 멤버 확정 출력
                        is_g1 = "g1-bg" if float(final_member['그룹']) == 1.0 else ""
                        badge = '<span class="badge">G1</span>' if float(final_member['그룹']) == 1.0 else ""
                        sid = str(int(float(final_member['학번']))); grade = str(int(float(final_member['학년'])))
                        placeholders[m_idx].markdown(f'<div class="member-row {is_g1}"><div><span class="member-name">{final_member["성명"]}</span>{badge}</div><div style="font-size:0.8em; color:gray;">{grade}학년 | {sid} | {final_member["학과"]}</div></div>', unsafe_allow_html=True)
                else:
                    # 이미 확정된 이전 팀들은 애니메이션 없이 즉시 표시
                    m_html = ""
                    for m in team_members:
                        is_g1 = "g1-bg" if float(m['그룹']) == 1.0 else ""
                        badge = '<span class="badge">G1</span>' if float(m['그룹']) == 1.0 else ""
                        sid = str(int(float(m['학번']))); grade = str(int(float(m['학년'])))
                        m_html += f'<div class="member-row {is_g1}"><div><span class="member-name">{m["성명"]}</span>{badge}</div><div style="font-size:0.8em; color:gray;">{grade}학년 | {sid} | {m["학과"]}</div></div>'
                    st.markdown(f'<div class="team-card"><div class="team-title">TEAM {i + 1}</div>{m_html}</div>', unsafe_allow_html=True)
