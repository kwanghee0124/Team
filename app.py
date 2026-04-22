import streamlit as st
import pandas as pd
import time
import random

st.set_page_config(page_title="오픈소스SW기초 팀 배정", layout="wide")

# CSS 스타일 (고정 보드 및 디자인)
st.markdown("""
    <style>
    .announcement-fixed-box {
        background: linear-gradient(135deg, #1a1a1a 0%, #2d3436 100%);
        border-radius: 25px; padding: 40px; margin-bottom: 20px;
        text-align: center; box-shadow: 0 15px 35px rgba(0,0,0,0.3);
        color: white; min-height: 400px; display: flex;
        flex-direction: column; justify-content: center; align-items: center;
        border: 2px solid #444;
    }
    .announcement-title { font-size: 1.8em; font-weight: 800; margin-bottom: 30px; color: #fab005; }
    .new-member-card {
        background: rgba(255, 255, 255, 0.1); border: 1px solid rgba(255,255,255,0.3);
        border-radius: 20px; padding: 25px; width: 280px; text-align: center;
    }
    .new-member-name { font-size: 2.5em; font-weight: 900; color: #fff; margin-bottom: 5px; }
    .new-member-info { font-size: 1.1em; color: #ccc; }
    
    .team-card {
        background-color: #ffffff; border-radius: 12px; padding: 20px;
        margin-bottom: 20px; border: 1px solid #e1e4e8;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05); min-height: 250px;
    }
    .team-title { color: #1f77b4; font-size: 1.3em; font-weight: bold; border-bottom: 2px solid #1f77b4; padding-bottom: 8px; margin-bottom: 15px; }
    .member-row { margin-bottom: 12px; padding: 10px; border-radius: 8px; min-height: 60px; display: flex; flex-direction: column; justify-content: center; }
    .g1-bg { background-color: #e8f4f8; border-left: 5px solid #1f77b4; }
    .gender-f { color: #ff6b6b; font-weight: bold; }
    .gender-m { color: #4dabf7; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

def create_balanced_teams(df_clean):
    # 그룹별 분리
    g1 = [x for x in df_clean.to_dict('records') if x['그룹'] == 1.0]
    g2 = [x for x in df_clean.to_dict('records') if x['그룹'] == 2.0]
    g3 = [x for x in df_clean.to_dict('records') if x['그룹'] == 3.0]

    # 성별 섞기 함수
    def get_gender_split(data):
        m = [x for x in data if x['성별'] == '남']
        f = [x for x in data if x['성별'] == '여']
        random.shuffle(m)
        random.shuffle(f)
        return m, f

    g1_m, g1_f = get_gender_split(g1)
    g2_m, g2_f = get_gender_split(g2)
    g3_m, g3_f = get_gender_split(g3)

    teams = []
    
    # 1. G2 없는 2개 팀 (최대한 여학생 분산)
    for _ in range(2):
        leader = g1_f.pop() if g1_f else g1_m.pop()
        m2 = g3_f.pop() if g3_f else g3_m.pop()
        m3 = g3_m.pop() if g3_m else g3_f.pop()
        teams.append([leader, m2, m3])

    # 2. 나머지 13개 팀 (남녀 교차 배정으로 밸런스 유도)
    for _ in range(13):
        tm = []
        # G1에서 팝 (여학생 우선)
        if g1_f: tm.append(g1_f.pop())
        elif g1_m: tm.append(g1_m.pop())
        
        # G2에서 팝 (남학생 우선 - 밸런스)
        if g2_m: tm.append(g2_m.pop())
        elif g2_f: tm.append(g2_f.pop())
        
        # G3에서 팝 (남은 성별 고려)
        if g3_f: tm.append(g3_f.pop())
        elif g3_m: tm.append(g3_m.pop())
        
        teams.append([x for x in tm if x])

    return teams

st.title("🎲 오픈소스 SW 기초 팀 배정")

uploaded_file = st.file_uploader("명단 CSV 업로드", type=["csv"])

if uploaded_file:
    # 데이터 로드 (사용자가 말한 컬럼 순서: 그룹, 순번, 학년, 학과, 학번, 성별, 성명)
    df_raw = pd.read_csv(uploaded_file, skiprows=7)
    
    # 인덱스 매핑: 0:그룹, 5:성별, 2:학년, 3:학과, 4:학번, 6:성명
    try:
        df_clean = df_raw.iloc[:, [0, 5, 2, 3, 4, 6]].dropna(subset=[df_raw.columns[0], df_raw.columns[6]])
        df_clean.columns = ['그룹', '성별', '학년', '학과', '학번', '성명']
    except Exception as e:
        st.error("CSV 파일의 컬럼 개수가 부족하거나 형식이 맞지 않습니다. 컬럼 순서를 다시 확인해주세요.")
        st.stop()

    if 'current_team_idx' not in st.session_state: st.session_state.current_team_idx = 0
    if 'teams_list' not in st.session_state: st.session_state.teams_list = []
    if 'stage' not in st.session_state: st.session_state.stage = "READY"

    # 보드 공간 고정
    announcement_placeholder = st.empty()
    if st.session_state.stage == "READY" and st.session_state.current_team_idx == 0:
        announcement_placeholder.markdown('<div class="announcement-fixed-box"><div class="announcement-title">대기 중...</div><p>팀 구성을 생성한 뒤 발표를 시작하세요.</p></div>', unsafe_allow_html=True)

    c_btn = st.columns([1, 4])
    if c_btn[0].button("🔥 전체 팀 구성 생성"):
        st.session_state.teams_list = create_balanced_teams(df_clean)
        st.session_state.current_team_idx = 0
        st.session_state.stage = "READY"
        st.rerun()

    if st.session_state.teams_list:
        if st.session_state.current_team_idx < 15:
            if st.session_state.stage == "READY":
                if st.button(f"➡️ {st.session_state.current_team_idx + 1}팀 발표 시작"):
                    st.session_state.stage = "DRAWING"
                    st.rerun()
            elif st.session_state.stage == "FINISHED":
                if st.button(f"✅ {st.session_state.current_team_idx + 1}팀 명단 추가"):
                    st.session_state.current_team_idx += 1
                    st.session_state.stage = "READY"
                    st.rerun()

        # 발표 로직
        if st.session_state.stage == "DRAWING":
            idx = st.session_state.current_team_idx
            members = st.session_state.teams_list[idx]
            confirmed_cards = ""
            for m_idx, target in enumerate(members):
                for _ in range(8):
                    temp_name = df_clean.sample(1).iloc[0]['성명']
                    r_html = f'<div class="new-member-card"><div style="font-size:1.8em; color:#fab005; font-weight:bold;">{temp_name}</div><div>추첨 중...</div></div>'
                    announcement_placeholder.markdown(f'<div class="announcement-fixed-box"><div class="announcement-title">📢 {idx+1}팀 멤버 추첨 중!</div><div style="display:flex; gap:20px;">{confirmed_cards}{r_html}</div></div>', unsafe_allow_html=True)
                    time.sleep(0.05)
                
                g_color = "#ff6b6b" if target['성별'] == '여' else "#4dabf7"
                confirmed_cards += f'<div class="new-member-card"><div class="new-member-name">{target["성명"]}</div><div style="color:{g_color}; font-weight:bold; font-size:1.2em;">{target["성별"]} | {int(target["학년"])}학년</div><div class="new-member-info">{target["학과"]}</div></div>'
                announcement_placeholder.markdown(f'<div class="announcement-fixed-box"><div class="announcement-title">📢 {idx+1}팀 멤버 추첨 중!</div><div style="display:flex; gap:20px;">{confirmed_cards}</div></div>', unsafe_allow_html=True)
                time.sleep(0.4)
            st.session_state.stage = "FINISHED"
            st.rerun()

        if st.session_state.stage == "FINISHED":
            idx = st.session_state.current_team_idx
            members = st.session_state.teams_list[idx]
            cards = "".join([f'<div class="new-member-card"><div class="new-member-name">{m["성명"]}</div><div style="color:{"#ff6b6b" if m["성별"]=="여" else "#4dabf7"}; font-weight:bold; font-size:1.2em;">{m["성별"]} | {int(m["학년"])}학년</div><div class="new-member-info">{m["학과"]}</div></div>' for m in members])
            announcement_placeholder.markdown(f'<div class="announcement-fixed-box"><div class="announcement-title">✨ {idx+1}팀 구성 완료! ✨</div><div style="display:flex; gap:20px;">{cards}</div></div>', unsafe_allow_html=True)

        # 확정 명단
        if st.session_state.current_team_idx > 0:
            st.divider()
            t_cols = st.columns(3)
            display_indices = list(range(st.session_state.current_team_idx))
            display_indices.reverse()
            for v_idx, r_idx in enumerate(display_indices):
                team = st.session_state.teams_list[r_idx]
                m_html = "".join([f'<div class="member-row {"g1-bg" if float(m["그룹"])==1.0 else ""}"><div><b style="font-size:1.1em;">{m["성명"]}</b> ({"<span class=\"gender-f\">여</span>" if m["성별"]=="여" else "<span class=\"gender-m\">남</span>"})</div><div style="font-size:0.85em; color:gray;">{int(m["학년"])}학년 | {m["학과"]}</div></div>' for m in team])
                t_cols[v_idx % 3].markdown(f'<div class="team-card"><div class="team-title">TEAM {r_idx+1}</div>{m_html}</div>', unsafe_allow_html=True)
