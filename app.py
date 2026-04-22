import streamlit as st
import pandas as pd
import time
import random

st.set_page_config(page_title="오픈소스SW기초 팀 배정", layout="wide")

st.markdown("""
    <style>
    .announcement-fixed-box {
        background: linear-gradient(135deg, #1a1a1a 0%, #2d3436 100%);
        border-radius: 25px; padding: 40px; margin-bottom: 20px;
        text-align: center; box-shadow: 0 15px 35px rgba(0,0,0,0.3);
        color: white; min-height: 420px; display: flex;
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

# --- 팀 빌딩 알고리즘 (성별 균등 분배 핵심 로직) ---
def create_perfectly_balanced_teams(df_clean):
    g1 = [x for x in df_clean.to_dict('records') if x['그룹'] == 1.0]
    g2 = [x for x in df_clean.to_dict('records') if x['그룹'] == 2.0]
    g3 = [x for x in df_clean.to_dict('records') if x['그룹'] == 3.0]

    random.shuffle(g1); random.shuffle(g2); random.shuffle(g3)

    num_teams = 15
    teams = [[] for _ in range(num_teams)]

    # [1] G1, G2 골격 짜기 (팀마다 G1, G2 1명씩 / G2 없으면 G1 저학년)
    num_g2 = len(g2)
    num_no_g2 = max(0, num_teams - num_g2)

    g1_low = [x for x in g1 if int(float(x['학년'])) < 4]
    g1_high = [x for x in g1 if int(float(x['학년'])) >= 4]

    # G2가 없는 팀(G3 2명)에는 무조건 G1 저학년 배치
    for i in range(num_no_g2):
        if g1_low: teams[i].append(g1_low.pop(0))
        elif g1_high: teams[i].append(g1_high.pop(0))

    # 나머지 팀에 남은 G1 모두 1명씩 배치
    g1_rem = g1_low + g1_high
    for i in range(num_no_g2, num_teams):
        if g1_rem: teams[i].append(g1_rem.pop(0))

    # [2] G2 배치 시 1차 성별 밸런싱
    g2_targets = teams[num_no_g2:num_teams]
    # G2 여학생을 먼저 배정하기 위해 정렬
    g2_sorted = sorted(g2, key=lambda x: 0 if x['성별'] == '여' else 1)
    
    for student in g2_sorted:
        # 배정 직전마다 '현재 여학생 수가 가장 적은 팀'을 맨 앞으로 정렬
        g2_targets.sort(key=lambda t: len([m for m in t if m['성별'] == '여']))
        g2_targets[0].append(student)

    # [3] G3 배치 시 최종 성별 밸런싱 (이 부분이 해결의 핵심입니다)
    g3_sorted = sorted(g3, key=lambda x: 0 if x['성별'] == '여' else 1)
    
    while g3_sorted:
        needs_member = [t for t in teams if len(t) < 3]
        if not needs_member: break
        
        student = g3_sorted.pop(0)

        if student['성별'] == '여':
            # 여학생은 여학생이 가장 '없는' 팀을 찾아 들어감
            needs_member.sort(key=lambda t: len([m for m in t if m['성별'] == '여']))
        else:
            # 남학생은 반대로 여학생이 '많은' 팀을 우선 채워 남녀 비율을 희석시킴
            needs_member.sort(key=lambda t: len([m for m in t if m['성별'] == '여']), reverse=True)

        needs_member[0].append(student)

    random.shuffle(teams)
    return teams

# --- 메인 UI ---
st.title("🎲 오픈소스 SW 기초 팀 배정 시스템")

uploaded_file = st.file_uploader("명단 CSV 업로드", type=["csv"])

if uploaded_file:
    df_raw = pd.read_csv(uploaded_file, skiprows=7)
    try:
        df_clean = df_raw.iloc[:, [0, 5, 2, 3, 4, 6]].dropna(subset=[df_raw.columns[0], df_raw.columns[6]])
        df_clean.columns = ['그룹', '성별', '학년', '학과', '학번', '성명']
    except:
        st.error("CSV 컬럼 구조가 맞지 않습니다.")
        st.stop()

    if 'current_team_idx' not in st.session_state: st.session_state.current_team_idx = 0
    if 'teams_list' not in st.session_state: st.session_state.teams_list = []
    if 'stage' not in st.session_state: st.session_state.stage = "READY"

    announcement_placeholder = st.empty()
    if st.session_state.stage == "READY" and st.session_state.current_team_idx == 0:
        announcement_placeholder.markdown('<div class="announcement-fixed-box"><div class="announcement-title">Welcome</div><p>팀 구성을 생성한 뒤 발표를 시작하세요.</p></div>', unsafe_allow_html=True)

    c_btn = st.columns([1, 4])
    if c_btn[0].button("🔥 전체 팀 구성 생성"):
        st.session_state.teams_list = create_perfectly_balanced_teams(df_clean)
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
                if st.button(f"✅ {st.session_state.current_team_idx + 1}팀 명단 확정"):
                    st.session_state.current_team_idx += 1
                    st.session_state.stage = "READY"
                    st.rerun()

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

    st.divider()
    with st.expander("👥 그룹별 학생 명단 보기"):
        c1, c2, c3 = st.columns(3)
        for g_num, col in zip([1, 2, 3], [c1, c2, c3]):
            g_data = df_clean[df_clean['그룹'] == float(g_num)].sort_values(by=['학년', '학번'])
            inner = "".join([f'<div class="student-card"><div style="color:#1f77b4; font-size:0.8em; font-weight:bold;">{r["학과"].replace("SW융합대학 ","")}</div><div style="font-weight:bold;">{r["성명"]} ({"여" if r["성별"]=="여" else "남"})</div><div style="font-size:0.75em; color:gray;">{int(r["학년"])}학년 | {str(int(float(r["학번"])))}</div></div>' for _, r in g_data.iterrows()])
            col.markdown(f'<div class="group-container"><h4>Group {g_num} ({len(g_data)}명)</h4>{inner}</div>', unsafe_allow_html=True)
