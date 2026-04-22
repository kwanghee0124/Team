import streamlit as st
import pandas as pd
import time
import random

st.set_page_config(page_title="오픈소스SW기초 팀 배정", layout="wide")

# CSS 스타일 정의
st.markdown("""
    <style>
    /* 1. 고정 발표 보드 디자인 (흔들림 방지) */
    .announcement-fixed-box {
        background: linear-gradient(135deg, #1a1a1a 0%, #2d3436 100%);
        border-radius: 25px; padding: 40px; margin-bottom: 20px;
        text-align: center; box-shadow: 0 15px 35px rgba(0,0,0,0.3);
        color: white; min-height: 420px; display: flex;
        flex-direction: column; justify-content: center; align-items: center;
        border: 2px solid #444;
    }
    .announcement-title { font-size: 1.8em; font-weight: 800; margin-bottom: 30px; color: #fab005; }
    
    /* 2. 발표 카드 디자인 (이름 크게) */
    .new-member-card {
        background: rgba(255, 255, 255, 0.1); border: 1px solid rgba(255,255,255,0.3);
        border-radius: 20px; padding: 25px; width: 280px; text-align: center;
    }
    .new-member-name { font-size: 2.5em; font-weight: 900; color: #fff; margin-bottom: 5px; }
    .new-member-info { font-size: 1.1em; color: #ccc; }
    
    /* 3. 하단 명단 카드 */
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
    
    /* 4. 그룹 현황 학생 카드 (2열 배치) */
    .student-card {
        background-color: #ffffff; border-radius: 8px; padding: 8px;
        margin: 4px; border: 1px solid #e1e4e8;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05); display: inline-block;
        width: calc(50% - 12px); vertical-align: top; text-align: left;
    }
    .group-container {
        background-color: #f1f3f5; border-radius: 15px; padding: 15px;
        margin-bottom: 20px; border: 2px solid #dee2e6;
    }
    .roulette-text { color: #fab005; font-size: 2em; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 팀 빌딩 알고리즘 ---
def create_balanced_teams(df_clean):
    def get_refined_split(group_num):
        data = [x for x in df_clean.to_dict('records') if x['그룹'] == float(group_num)]
        if group_num == 1:
            low = [x for x in data if int(float(x['학년'])) < 4]
            high = [x for x in data if int(float(x['학년'])) >= 4]
            random.shuffle(low); random.shuffle(high)
            return low, high
        m = [x for x in data if x['성별'] == '남']
        f = [x for x in data if x['성별'] == '여']
        random.shuffle(m); random.shuffle(f)
        return m, f

    g1_low, g1_high = get_refined_split(1)
    g2_m, g2_f = get_refined_split(2)
    g3_m, g3_f = get_refined_split(3)

    num_teams = 15
    teams = [[] for _ in range(num_teams)]

    # [1] G2가 들어가지 않을 팀(G3가 2명 들어갈 팀) 계산
    num_g2 = len(g2_m) + len(g2_f)
    num_no_g2_teams = max(0, num_teams - num_g2)
    
    # [2] 리더격(G1/G2) 배치
    # G2 없는 팀(G3 2명 팀)에는 무조건 G1 저학년 배치
    for i in range(num_no_g2_teams):
        if g1_low: teams[i].append(g1_low.pop(0))
        elif g1_high: teams[i].append(g1_high.pop(0))

    # 나머지 팀에는 G1과 G2를 배타적으로 배치 (겹치지 않게)
    g2_pool = g2_f + g2_m
    g1_rem = g1_high + g1_low
    for i in range(num_no_g2_teams, num_teams):
        if g1_rem: teams[i].append(g1_rem.pop(0))
        if g2_pool: teams[i].append(g2_pool.pop(0))

    # [3] 여학생 분산 배치 (팀당 여학생 최대 2명)
    all_assigned_ids = [m['학번'] for t in teams for m in t]
    rem_f = [x for x in (g3_f + g2_f + g1_low + g1_high) if x['학번'] not in all_assigned_ids and x['성별'] == '여']
    rem_m = [x for x in (g3_m + g2_m + g1_low + g1_high) if x['학번'] not in all_assigned_ids and x['성별'] == '남']
    random.shuffle(rem_f); random.shuffle(rem_m)

    for i in range(num_teams):
        while len(teams[i]) < 3:
            curr_f = len([m for m in teams[i] if m['성별'] == '여'])
            if curr_f < 2 and rem_f:
                teams[i].append(rem_f.pop(0))
            elif rem_m:
                teams[i].append(rem_m.pop(0))
            elif rem_f: # 남학생 부족 시 어쩔 수 없이 3여 방지보다 인원 우선
                teams[i].append(rem_f.pop(0))
            else: break
            
    random.shuffle(teams)
    return teams

# --- 메인 UI ---
st.title("🎲 오픈소스 SW 기초 팀 배정 시스템")

uploaded_file = st.file_uploader("명단 CSV 업로드", type=["csv"])

if uploaded_file:
    df_raw = pd.read_csv(uploaded_file, skiprows=7)
    try:
        # 순서: 그룹(0), 순번(1), 학년(2), 학과(3), 학번(4), 성별(5), 성명(6)
        df_clean = df_raw.iloc[:, [0, 5, 2, 3, 4, 6]].dropna(subset=[df_raw.columns[0], df_raw.columns[6]])
        df_clean.columns = ['그룹', '성별', '학년', '학과', '학번', '성명']
    except:
        st.error("CSV 컬럼 구조가 맞지 않습니다. (그룹, 순번, 학년, 학과, 학번, 성별, 성명 순서여야 합니다)")
        st.stop()

    if 'current_team_idx' not in st.session_state: st.session_state.current_team_idx = 0
    if 'teams_list' not in st.session_state: st.session_state.teams_list = []
    if 'stage' not in st.session_state: st.session_state.stage = "READY"

    # 보드 고정
    announcement_placeholder = st.empty()
    if st.session_state.stage == "READY" and st.session_state.current_team_idx == 0:
        announcement_placeholder.markdown('<div class="announcement-fixed-box"><div class="announcement-title">Welcome</div><p>팀 구성을 생성한 뒤 발표를 시작하세요.</p></div>', unsafe_allow_html=True)

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
                if st.button(f"✅ {st.session_state.current_team_idx + 1}팀 명단 확정 및 추가"):
                    st.session_state.current_team_idx += 1
                    st.session_state.stage = "READY"
                    st.rerun()

        # 발표 애니메이션
        if st.session_state.stage == "DRAWING":
            idx = st.session_state.current_team_idx
            members = st.session_state.teams_list[idx]
            confirmed_cards = ""
            for m_idx, target in enumerate(members):
                for _ in range(7):
                    temp_name = df_clean.sample(1).iloc[0]['성명']
                    r_html = f'<div class="new-member-card"><div class="roulette-text">{temp_name}</div><div>추첨 중...</div></div>'
                    announcement_placeholder.markdown(f'<div class="announcement-fixed-box"><div class="announcement-title">📢 {idx+1}팀 멤버 추첨 중!</div><div style="display:flex; gap:20px;">{confirmed_cards}{r_html}</div></div>', unsafe_allow_html=True)
                    time.sleep(0.06)
                
                g_color = "#ff6b6b" if target['성별'] == '여' else "#4dabf7"
                confirmed_cards += f'<div class="new-member-card"><div class="new-member-name">{target["성명"]}</div><div style="color:{g_color}; font-weight:bold; font-size:1.2em;">{target["성별"]} | {int(target["학년"])}학년</div><div class="new-member-info">G{int(target["그룹"])} | {target["학과"]}</div></div>'
                announcement_placeholder.markdown(f'<div class="announcement-fixed-box"><div class="announcement-title">📢 {idx+1}팀 멤버 추첨 중!</div><div style="display:flex; gap:20px;">{confirmed_cards}</div></div>', unsafe_allow_html=True)
                time.sleep(0.4)
            st.session_state.stage = "FINISHED"
            st.rerun()

        if st.session_state.stage == "FINISHED":
            idx = st.session_state.current_team_idx
            members = st.session_state.teams_list[idx]
            cards = "".join([f'<div class="new-member-card"><div class="new-member-name">{m["성명"]}</div><div style="color:{"#ff6b6b" if m["성별"]=="여" else "#4dabf7"}; font-weight:bold; font-size:1.2em;">{m["성별"]} | {int(m["학년"])}학년</div><div class="new-member-info">G{int(m["그룹"])} | {m["학과"]}</div></div>' for m in members])
            announcement_placeholder.markdown(f'<div class="announcement-fixed-box"><div class="announcement-title">✨ {idx+1}팀 구성 완료! ✨</div><div style="display:flex; gap:20px;">{cards}</div></div>', unsafe_allow_html=True)

        # 하단 리스트 (최신순)
        if st.session_state.current_team_idx > 0:
            st.divider()
            st.subheader("📋 확정된 팀 명단 (최신순)")
            t_cols = st.columns(3)
            indices = list(range(st.session_state.current_team_idx))
            indices.reverse()
            for v_idx, r_idx in enumerate(indices):
                team = st.session_state.teams_list[r_idx]
                m_html = "".join([f'<div class="member-row {"g1-bg" if float(m["그룹"])==1.0 else ""}"><div><b style="font-size:1.1em;">{m["성명"]}</b> ({"<span class=\"gender-f\">여</span>" if m["성별"]=="여" else "<span class=\"gender-m\">남</span>"})</div><div style="font-size:0.85em; color:gray;">G{int(m["그룹"])} | {int(m["학년"])}학년 | {m["학과"]}</div></div>' for m in team])
                t_cols[v_idx % 3].markdown(f'<div class="team-card"><div class="team-title">TEAM {r_idx+1}</div>{m_html}</div>', unsafe_allow_html=True)

    # 그룹 현황 리스트
    st.divider()
    with st.expander("👥 그룹별 학생 명단 보기"):
        c1, c2, c3 = st.columns(3)
        for g_num, col in zip([1, 2, 3], [c1, c2, c3]):
            g_data = df_clean[df_clean['그룹'] == float(g_num)].sort_values(by=['학년', '학번'])
            inner = "".join([f'<div class="student-card"><div style="color:#1f77b4; font-size:0.8em; font-weight:bold;">{r["학과"].replace("SW융합대학 ","")}</div><div style="font-weight:bold;">{r["성명"]} ({"여" if r["성별"]=="여" else "남"})</div><div style="font-size:0.75em; color:gray;">{int(r["학년"])}학년 | {str(int(float(r["학번"])))}</div></div>' for _, r in g_data.iterrows()])
            col.markdown(f'<div class="group-container"><h4>Group {g_num} ({len(g_data)}명)</h4>{inner}</div>', unsafe_allow_html=True)
