import streamlit as st
import pandas as pd
import time
import random

st.set_page_config(page_title="오픈소스SW기초 팀 배정", layout="wide")

# (기존 CSS 스타일 유지)
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

def create_strictly_balanced_teams(df_clean):
    # 1. 그룹별/성별 데이터 분리
    def get_split(group_num):
        group_data = [x for x in df_clean.to_dict('records') if x['그룹'] == float(group_num)]
        m = [x for x in group_data if x['성별'] == '남']
        f = [x for x in group_data if x['성별'] == '여']
        random.shuffle(m); random.shuffle(f)
        return m, f

    g1_m, g1_f = get_split(1)
    g2_m, g2_f = get_split(2)
    g3_m, g3_f = get_split(3)

    num_teams = 15
    teams = [[] for _ in range(num_teams)]

    # [규칙 1] 모든 팀에 G1 또는 G2를 1명씩 배타적으로 배정 (리더격)
    # G1과 G2가 섞이지 않도록 순차적으로 풀(Pool) 구성
    leader_pool = (g1_f + g1_m) + (g2_f + g2_m)
    
    for i in range(num_teams):
        if leader_pool:
            teams[i].append(leader_pool.pop(0))

    # [규칙 2] 여학생 분산 배치 (팀당 여학생 최대 2명 제한)
    # 아직 배치되지 않은 나머지 여학생들 모으기
    all_remaining_f = [x for x in (g1_f + g1_m + g2_f + g2_m + g3_f + g3_m) if x not in [m for t in teams for m in t] and x['성별'] == '여']
    random.shuffle(all_remaining_f)

    # 모든 팀을 돌면서 여학생이 1명도 없는 팀에 우선 배치
    for i in range(num_teams):
        if not any(m['성별'] == '여' for m in teams[i]):
            if all_remaining_f:
                teams[i].append(all_remaining_f.pop(0))

    # [규칙 3] 나머지 인원 채우기 (G3 위주)
    # 아직 아무 팀에도 속하지 않은 모든 인원 모으기
    all_remaining_students = [x for x in (g1_m + g1_f + g2_m + g2_f + g3_m + g3_f) if x not in [m for t in teams for m in t]]
    random.shuffle(all_remaining_students)

    for i in range(num_teams):
        while len(teams[i]) < 3:
            if not all_remaining_students: break
            
            # 현재 팀의 여학생 수 확인
            current_f_count = len([m for m in teams[i] if m['성별'] == '여'])
            
            # 다음 뽑을 학생이 여학생인데 이미 팀에 여학생이 2명이면 패스하고 남학생 찾기
            next_student = all_remaining_students[0]
            if next_student['성별'] == '여' and current_f_count >= 2:
                # 남학생을 찾아서 먼저 뽑음
                male_idx = next((idx for idx, s in enumerate(all_remaining_students) if s['성별'] == '남'), None)
                if male_idx is not None:
                    teams[i].append(all_remaining_students.pop(male_idx))
                else:
                    # 남학생이 아예 없으면 어쩔 수 없이 여학생 추가 (인원수 맞추기 위해)
                    teams[i].append(all_remaining_students.pop(0))
            else:
                teams[i].append(all_remaining_students.pop(0))

    random.shuffle(teams)
    return teams

# (UI 부분: 기존과 동일하되 create_strictly_balanced_teams 호출)
st.title("🎲 오픈소스 SW 기초 팀 배정 (그룹 배타 조건)")

uploaded_file = st.file_uploader("명단 CSV 업로드", type=["csv"])

if uploaded_file:
    df_raw = pd.read_csv(uploaded_file, skiprows=7)
    try:
        df_clean = df_raw.iloc[:, [0, 5, 2, 3, 4, 6]].dropna(subset=[df_raw.columns[0], df_raw.columns[6]])
        df_clean.columns = ['그룹', '성별', '학년', '학과', '학번', '성명']
    except:
        st.error("CSV 컬럼 구조를 확인해주세요.")
        st.stop()

    if 'current_team_idx' not in st.session_state: st.session_state.current_team_idx = 0
    if 'teams_list' not in st.session_state: st.session_state.teams_list = []
    if 'stage' not in st.session_state: st.session_state.stage = "READY"

    announcement_placeholder = st.empty()
    if st.session_state.stage == "READY" and st.session_state.current_team_idx == 0:
        announcement_placeholder.markdown('<div class="announcement-fixed-box"><div class="announcement-title">대기 중...</div><p>전체 팀 구성을 생성해주세요.</p></div>', unsafe_allow_html=True)

    if st.button("🔥 전체 팀 구성 생성"):
        st.session_state.teams_list = create_strictly_balanced_teams(df_clean)
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
                confirmed_cards += f'<div class="new-member-card"><div class="new-member-name">{target["성명"]}</div><div style="color:{g_color}; font-weight:bold; font-size:1.2em;">{target["성별"]} | {int(target["학년"])}학년</div><div class="new-member-info">그룹 {int(target["그룹"])} | {target["학과"]}</div></div>'
                announcement_placeholder.markdown(f'<div class="announcement-fixed-box"><div class="announcement-title">📢 {idx+1}팀 멤버 추첨 중!</div><div style="display:flex; gap:20px;">{confirmed_cards}</div></div>', unsafe_allow_html=True)
                time.sleep(0.4)
            st.session_state.stage = "FINISHED"
            st.rerun()

        if st.session_state.stage == "FINISHED":
            idx = st.session_state.current_team_idx
            members = st.session_state.teams_list[idx]
            cards = "".join([f'<div class="new-member-card"><div class="new-member-name">{m["성명"]}</div><div style="color:{"#ff6b6b" if m["성별"]=="여" else "#4dabf7"}; font-weight:bold; font-size:1.2em;">{m["성별"]} | {int(m["학년"])}학년</div><div class="new-member-info">그룹 {int(m["그룹"])} | {m["학과"]}</div></div>' for m in members])
            announcement_placeholder.markdown(f'<div class="announcement-fixed-box"><div class="announcement-title">✨ {idx+1}팀 구성 완료! ✨</div><div style="display:flex; gap:25px;">{cards}</div></div>', unsafe_allow_html=True)

        if st.session_state.current_team_idx > 0:
            st.divider()
            t_cols = st.columns(3)
            display_indices = list(range(st.session_state.current_team_idx))
            display_indices.reverse()
            for v_idx, r_idx in enumerate(display_indices):
                team = st.session_state.teams_list[r_idx]
                m_html = "".join([f'<div class="member-row {"g1-bg" if float(m["그룹"])==1.0 else ""}"><div><b style="font-size:1.1em;">{m["성명"]}</b> ({"<span class=\"gender-f\">여</span>" if m["성별"]=="여" else "<span class=\"gender-m\">남</span>"})</div><div style="font-size:0.85em; color:gray;">G{int(m["그룹"])} | {int(m["학년"])}학년 | {m["학과"]}</div></div>' for m in team])
                t_cols[v_idx % 3].markdown(f'<div class="team-card"><div class="team-title">TEAM {r_idx+1}</div>{m_html}</div>', unsafe_allow_html=True)
