import streamlit as st
import pandas as pd
import time
import random

st.set_page_config(page_title="오픈소스SW기초 팀 배정", layout="wide")

# CSS 스타일 정의
st.markdown("""
    <style>
    /* 1. 발표 전용 보드 디자인 개선 */
    .announcement-container {
        background: linear-gradient(135deg, #1f77b4 0%, #2c3e50 100%);
        border-radius: 25px;
        padding: 40px;
        margin-bottom: 20px;
        text-align: center;
        box-shadow: 0 15px 35px rgba(0,0,0,0.2);
        color: white;
        min-height: 380px; /* 높이 고정으로 레이아웃 흔들림 방지 */
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        border: 4px solid #ffffff33;
    }
    .announcement-title { 
        font-size: 1.8em; 
        font-weight: 800; 
        margin-bottom: 30px; 
        letter-spacing: -1px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    /* 2. 학생 카드 (발표 보드용) - 더 크게 */
    .new-member-card {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(10px);
        border: 2px solid rgba(255,255,255,0.4);
        border-radius: 20px;
        padding: 25px;
        width: 280px;
        text-align: center;
        transition: all 0.5s ease;
    }
    .new-member-name {
        font-size: 2.5em; /* 이름 대폭 확대 */
        font-weight: 900;
        margin-bottom: 10px;
        color: #ffffff;
    }
    .new-member-info {
        font-size: 1.1em;
        color: #e0e0e0;
    }

    /* 3. 리스트 카드 스타일 */
    .team-card {
        background-color: #ffffff; border-radius: 12px; padding: 20px;
        margin-bottom: 20px; border: 1px solid #e1e4e8;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05); min-height: 250px;
    }
    .team-title { color: #1f77b4; font-size: 1.3em; font-weight: bold; border-bottom: 2px solid #1f77b4; padding-bottom: 8px; margin-bottom: 15px; }
    .member-row { margin-bottom: 12px; padding: 10px; border-radius: 8px; min-height: 60px; display: flex; flex-direction: column; justify-content: center; }
    .g1-bg { background-color: #e8f4f8; border-left: 5px solid #1f77b4; }
    
    .roulette-text { 
        font-size: 1.8em; 
        font-weight: bold; 
        color: #ffda44; 
        text-shadow: 0 0 10px rgba(255,218,68,0.5);
    }
    
    /* 그룹 현황 그리드 */
    .student-card {
        background-color: #ffffff; border-radius: 8px; padding: 8px;
        margin: 4px; border: 1px solid #e1e4e8;
        display: inline-block; width: calc(50% - 12px); text-align: left;
    }
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

st.title("🎲 오픈소스 SW 기초 팀 배정")

uploaded_file = st.file_uploader("명단 CSV 업로드", type=["csv"])

if uploaded_file:
    df_raw = pd.read_csv(uploaded_file, skiprows=7)
    df_clean = df_raw.iloc[:, [0, 2, 3, 4, 37]].dropna(subset=[df_raw.columns[0], df_raw.columns[37]])
    df_clean.columns = ['그룹', '학년', '학과', '학번', '성명']

    # 1. 상태 관리
    if 'current_team_idx' not in st.session_state: st.session_state.current_team_idx = 0
    if 'teams_list' not in st.session_state: st.session_state.teams_list = []
    if 'stage' not in st.session_state: st.session_state.stage = "READY" # READY, DRAWING, FINISHED

    # 상단 발표 공간 고정
    announcement_placeholder = st.empty()

    # 제어 버튼
    col_btn1, col_btn2 = st.columns([1, 4])
    if col_btn1.button("🔥 전체 팀 구성 생성"):
        st.session_state.teams_list = get_final_teams(df_clean)
        st.session_state.current_team_idx = 0
        st.session_state.stage = "READY"
        st.rerun()

    if st.session_state.teams_list:
        # 버튼 상태 변경 로직
        if st.session_state.current_team_idx < 15:
            if st.session_state.stage == "READY":
                if st.button(f"➡️ {st.session_state.current_team_idx + 1}팀 발표 시작"):
                    st.session_state.stage = "DRAWING"
                    st.rerun()
            elif st.session_state.stage == "FINISHED":
                if st.button(f"✅ {st.session_state.current_team_idx + 1}팀 명단에 추가"):
                    st.session_state.current_team_idx += 1
                    st.session_state.stage = "READY"
                    st.rerun()

        # 2. 발표 애니메이션 실행
        if st.session_state.stage == "DRAWING":
            idx = st.session_state.current_team_idx
            members = st.session_state.teams_list[idx]
            confirmed_cards = ""
            
            for m_idx, target in enumerate(members):
                # 룰렛 애니메이션
                for _ in range(10):
                    temp_name = df_clean.sample(1).iloc[0]['성명']
                    roulette_html = f'<div class="new-member-card"><div class="roulette-text">{temp_name}</div><div class="new-member-info">추첨 중...</div></div>'
                    announcement_placeholder.markdown(f'<div class="announcement-container"><div class="announcement-title">🎊 {idx+1}팀 멤버를 추첨합니다!</div><div style="display:flex; gap:25px;">{confirmed_cards}{roulette_html}</div></div>', unsafe_allow_html=True)
                    time.sleep(0.05)
                
                # 멤버 확정
                badge = '<span style="background:#fff; color:#1f77b4; padding:2px 8px; border-radius:10px; font-size:0.4em; vertical-align:middle; margin-left:10px;">G1</span>' if float(target['그룹']) == 1.0 else ""
                confirmed_cards += f'<div class="new-member-card"><div class="new-member-name">{target["성명"]}{badge}</div><div class="new-member-info">{int(target["학년"])}학년 | {target["학과"]}</div></div>'
                announcement_placeholder.markdown(f'<div class="announcement-container"><div class="announcement-title">🎊 {idx+1}팀 멤버를 추첨합니다!</div><div style="display:flex; gap:25px;">{confirmed_cards}</div></div>', unsafe_allow_html=True)
                time.sleep(0.5)
            
            st.session_state.stage = "FINISHED"
            st.rerun()

        # FINISHED 상태일 때 보드 유지 (사용자가 '명단 추가' 누르기 전까지)
        if st.session_state.stage == "FINISHED":
            idx = st.session_state.current_team_idx
            members = st.session_state.teams_list[idx]
            cards = "".join([f'<div class="new-member-card"><div class="new-member-name">{m["성명"]}</div><div class="new-member-info">{int(m["학년"])}학년 | {m["학과"]}</div></div>' for m in members])
            announcement_placeholder.markdown(f'<div class="announcement-container"><div class="announcement-title">✨ {idx+1}팀 구성 완료! ✨</div><div style="display:flex; gap:25px;">{cards}</div></div>', unsafe_allow_html=True)

        # 3. 하단 명단 (최신순)
        if st.session_state.current_team_idx > 0:
            st.divider()
            st.subheader("📋 확정 명단")
            t_cols = st.columns(3)
            display_indices = list(range(st.session_state.current_team_idx))
            display_indices.reverse()

            for v_idx, r_idx in enumerate(display_indices):
                team = st.session_state.teams_list[r_idx]
                m_html = "".join([f'<div class="member-row {"g1-bg" if float(m["그룹"])==1.0 else ""}"><div><b>{m["성명"]}</b> {"<small>(G1)</small>" if float(m["그룹"])==1.0 else ""}</div><div style="font-size:0.8em; color:gray;">{int(m["학년"])}학년 | {m["학과"]}</div></div>' for m in team])
                t_cols[v_idx % 3].markdown(f'<div class="team-card"><div class="team-title">TEAM {r_idx+1}</div>{m_html}</div>', unsafe_allow_html=True)

    st.divider()
    # 그룹 현황 (하단 배치)
    with st.expander("👥 그룹별 학생 명단 보기"):
        c1, c2, c3 = st.columns(3)
        for g_num, col in zip([1, 2, 3], [c1, c2, c3]):
            g_data = df_clean[df_clean['그룹'] == float(g_num)].sort_values(by='성명')
            inner = "".join([f'<div class="student-card"><b>{r["성명"]}</b><br><small>{r["학과"].replace("SW융합대학 ","")}</small></div>' for _, r in g_data.iterrows()])
            col.markdown(f'<div style="background:#f8f9fa; padding:15px; border-radius:15px;"><h4>Group {g_num}</h4>{inner}</div>', unsafe_allow_html=True)
