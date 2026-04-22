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
        margin-bottom: 20px; border: 2px solid #1f77b4; /* 최신 팀 강조를 위해 테두리 색상 유지 */
        box-shadow: 0 4px 10px rgba(0,0,0,0.1); min-height: 280px;
    }
    .old-team-card {
        background-color: #ffffff; border-radius: 12px; padding: 20px;
        margin-bottom: 20px; border: 1px solid #e1e4e8;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05); min-height: 280px;
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
        inner_html = "".join([f'<div class="student-card"><div class="st-dept">{r["학과"].replace("SW융합대학 ", "")}</div><div class="st-name">{r["성명"]}</div><div class="st-info">{int(r["학년"])}학년 | {str(int(float(r["학번"])))}</div></div>' for _, r in group_data.iterrows()])
        col.markdown(f'<div class="group-container"><h4 style="text-align:center;">Group {g_num}</h4>{inner_html}</div>', unsafe_allow_html=True)

    st.divider()

    # 2. 팀 추첨 로직 및 상태 관리
    if 'current_team_idx' not in st.session_state: st.session_state.current_team_idx = 0
    if 'teams_list' not in st.session_state: st.session_state.teams_list = []
    if 'last_drawn_idx' not in st.session_state: st.session_state.last_drawn_idx = -1

    if st.button("🔥 전체 팀 구성 생성"):
        st.session_state.teams_list = get_final_teams(df_clean)
        st.session_state.current_team_idx = 0
        st.session_state.last_drawn_idx = -1
        st.rerun()

    if st.session_state.teams_list:
        btn_placeholder = st.empty()
        
        if st.session_state.current_team_idx < 15:
            if btn_placeholder.button(f"➡️ {st.session_state.current_team_idx + 1}팀 추첨하기"):
                st.session_state.current_team_idx += 1
        
        st.subheader(f"🎊 배정 결과 (최신순)")
        t_cols = st.columns(3)
        
        # [수정 포인트] 0부터 idx까지가 아니라, idx-1부터 0까지 역순(reversed)으로 출력
        display_indices = list(range(st.session_state.current_team_idx))
        display_indices.reverse() # 최신 팀이 앞으로 오도록 인덱스 뒤집기

        for visual_idx, real_idx in enumerate(display_indices):
            with t_cols[visual_idx % 3]:
                team_members = st.session_state.teams_list[real_idx]
                
                # 방금 뽑힌 팀 (가장 큰 인덱스)인 경우 애니메이션 실행
                if real_idx == st.session_state.current_team_idx - 1 and st.session_state.last_drawn_idx < real_idx:
                    placeholder = st.empty()
                    confirmed_html = ""
                    
                    for m_idx, final_m in enumerate(team_members):
                        for _ in range(5):
                            temp = df_clean.sample(1).iloc[0]
                            temp_row = f'<div class="member-row" style="border: 1px dashed #ccc;"><div class="roulette-text">🎲 추첨 중...</div><div style="color:#aaa;">{temp["성명"]}</div></div>'
                            placeholder.markdown(f'<div class="team-card"><div class="team-title">TEAM {real_idx+1} (NEW!)</div>{confirmed_html}{temp_row}</div>', unsafe_allow_html=True)
                            time.sleep(0.06)
                        
                        is_g1 = "g1-bg" if float(final_m['그룹']) == 1.0 else ""
                        badge = '<span class="badge">G1</span>' if float(final_m['그룹']) == 1.0 else ""
                        confirmed_html += f'<div class="member-row {is_g1}"><div><span class="member-name">{final_m["성명"]}</span>{badge}</div><div class="member-info" style="font-size:0.8em; color:gray;">{int(final_m["학년"])}학년 | {str(int(float(final_m["학번"])))} | {final_m["학과"]}</div></div>'
                        placeholder.markdown(f'<div class="team-card"><div class="team-title">TEAM {real_idx+1} (NEW!)</div>{confirmed_html}</div>', unsafe_allow_html=True)
                    
                    st.session_state.last_drawn_idx = real_idx
                    st.rerun() 
                else:
                    # 기존 팀들은 번호는 유지하되 위치만 밀림
                    m_html = "".join([f'<div class="member-row {"g1-bg" if float(m["그룹"])==1.0 else ""}"><div><span class="member-name">{m["성명"]}</span>{"<span class=\"badge\">G1</span>" if float(m["그룹"])==1.0 else ""}</div><div style="font-size:0.8em; color:gray;">{int(m["학년"])}학년 | {str(int(float(m["학번"])))} | {m["학과"]}</div></div>' for m in team_members])
                    st.markdown(f'<div class="old-team-card"><div class="team-title" style="color:#666; border-bottom: 2px solid #ccc;">TEAM {real_idx+1}</div>{m_html}</div>', unsafe_allow_html=True)
