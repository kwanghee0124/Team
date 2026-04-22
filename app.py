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
        border-radius: 20px; padding: 25px; width: 280px; text-align: center; position: relative;
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
    
    .leader-bg { background-color: #fff9db; border-left: 5px solid #fab005; } 
    .normal-bg { background-color: #f8f9fa; border-left: 5px solid #ced4da; }
    
    .student-card {
        background-color: #ffffff; border-radius: 8px; padding: 8px;
        margin: 4px; border: 1px solid #e1e4e8; display: inline-block;
        width: calc(50% - 12px); vertical-align: top; text-align: left;
    }
    .group-container {
        background-color: #f1f3f5; border-radius: 15px; padding: 15px;
        margin-bottom: 20px; border: 2px solid #dee2e6;
    }
    .roulette-text { color: #fab005; font-size: 2em; font-weight: bold; }
    
    /* 빠친코 애니메이션용 스타일 */
    .slot-machine { font-size: 5em; font-weight: bold; letter-spacing: 15px; text-shadow: 2px 2px 10px rgba(0,0,0,0.5); }
    </style>
    """, unsafe_allow_html=True)

def create_perfectly_balanced_teams(df_clean):
    g1 = [x for x in df_clean.to_dict('records') if x['그룹'] == 1.0]
    g2 = [x for x in df_clean.to_dict('records') if x['그룹'] == 2.0]
    g3 = [x for x in df_clean.to_dict('records') if x['그룹'] == 3.0]

    random.shuffle(g1); random.shuffle(g2); random.shuffle(g3)

    g1_low = [x for x in g1 if int(float(x['학년'])) < 4]
    g1_high = [x for x in g1 if int(float(x['학년'])) >= 4]

    g2_m = [x for x in g2 if x['성별'] == '남']
    g2_f = [x for x in g2 if x['성별'] == '여']

    num_teams = 15
    teams = [[] for _ in range(num_teams)]

    num_g2 = len(g2)
    num_no_g2 = max(0, num_teams - num_g2)

    for i in range(num_no_g2):
        if g1_low: teams[i].append(g1_low.pop(0))
        elif g1_high: teams[i].append(g1_high.pop(0))

    g1_rem = g1_low + g1_high
    random.shuffle(g1_rem)
    for i in range(num_no_g2, num_teams):
        if g1_rem: teams[i].append(g1_rem.pop(0))

    for i in range(num_no_g2, num_teams):
        g1_leader = teams[i][0] 
        if g1_leader['성별'] == '남':
            if g2_f: teams[i].append(g2_f.pop(0))
            elif g2_m: teams[i].append(g2_m.pop(0))
        else:
            if g2_m: teams[i].append(g2_m.pop(0))
            elif g2_f: teams[i].append(g2_f.pop(0))

    leftovers = g1_rem + g2_m + g2_f + g3
    f_left = [x for x in leftovers if x['성별'] == '여']
    m_left = [x for x in leftovers if x['성별'] == '남']

    random.shuffle(f_left); random.shuffle(m_left)

    for student in f_left:
        valid_teams = [t for t in teams if len(t) < 3 and len([m for m in t if m['성별'] == '여']) < 2]
        if not valid_teams: 
            valid_teams = [t for t in teams if len(t) < 3]
        if valid_teams:
            valid_teams.sort(key=lambda t: (len([m for m in t if m['성별'] == '여']), len(t)))
            valid_teams[0].append(student)

    for student in m_left:
        valid_teams = [t for t in teams if len(t) < 3]
        if valid_teams:
            valid_teams.sort(key=lambda t: len(t))
            valid_teams[0].append(student)

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
        df_clean['학과'] = df_clean['학과'].str.replace('SW융합대학 ', '').str.replace('프리무스국제대학 ', '')
        df_clean['그룹'] = df_clean['그룹'].astype(float) 
        
        df_clean = df_clean.sort_values(by=['그룹', '성명']).reset_index(drop=True)
    except:
        st.error("CSV 컬럼 구조가 맞지 않습니다.")
        st.stop()

    # ==========================================
    # 1. 상단: 명단 수정창 (기본 닫힘) & 현황 상시 노출
    # ==========================================
    
    # 수정창만 최소화 (기본 닫힘)
    with st.expander("📝 전체 학생 명단 확인 및 수정 (클릭하여 열기)", expanded=False):
        st.info("💡 표에서 학생의 **'그룹' 열을 더블클릭**하여 1.0, 2.0, 3.0 중 하나로 직접 변경할 수 있습니다. 수정한 즉시 현황에 반영됩니다.")
        edited_df = st.data_editor(
            df_clean,
            use_container_width=True,
            hide_index=True,
            column_config={
                "그룹": st.column_config.SelectboxColumn(
                    "그룹 (더블클릭)",
                    help="학생의 그룹을 재배치합니다.",
                    options=[1.0, 2.0, 3.0],
                    required=True
                )
            }
        )
        
    st.divider()
    
    # 그룹별 학생 현황은 밖으로 빼서 상시 노출
    st.subheader("📊 현재 그룹별 학생 분포")
    
    c1, c2, c3 = st.columns(3)
    for g_num, col in zip([1, 2, 3], [c1, c2, c3]):
        g_data = edited_df[edited_df['그룹'] == float(g_num)].sort_values(by=['학년', '학번'])
        inner = ""
        for _, r in g_data.iterrows():
            role_badge = '<span style="color:#fab005; font-size:0.85em; margin-left:5px;">👑 리더</span>' if g_num == 1 else ''
            inner += f'<div class="student-card"><div style="color:#1f77b4; font-size:0.8em; font-weight:bold;">{r["학과"]}</div><div style="font-weight:bold;">{r["성명"]}{role_badge}</div><div style="font-size:0.75em; color:gray;">{int(r["학년"])}학년 | {str(int(float(r["학번"])))}</div></div>'
        
        group_title = f"Group 1 (👑 리더 그룹, {len(g_data)}명)" if g_num == 1 else f"Group {g_num} ({len(g_data)}명)"
        col.markdown(f'<div class="group-container"><h4>{group_title}</h4>{inner}</div>', unsafe_allow_html=True)
            
    st.divider()

    # ==========================================
    # 2. 하단: 본격적인 팀 추첨 및 발표 영역
    # ==========================================
    if 'current_team_idx' not in st.session_state: st.session_state.current_team_idx = 0
    if 'teams_list' not in st.session_state: st.session_state.teams_list = []
    if 'stage' not in st.session_state: st.session_state.stage = "READY"

    announcement_placeholder = st.empty()
    
    if st.session_state.stage == "READY":
        if st.session_state.current_team_idx == 0:
            announcement_placeholder.markdown('<div class="announcement-fixed-box"><div class="announcement-title">Welcome</div><p style="color:#ccc; font-size:1.2em;">위에서 명단 확인 및 수정을 마친 뒤, 아래 버튼을 눌러 전체 팀 구성을 생성하세요.</p></div>', unsafe_allow_html=True)
        elif st.session_state.current_team_idx < 15:
            announcement_placeholder.markdown(f'<div class="announcement-fixed-box"><div class="announcement-title">✔️ {st.session_state.current_team_idx}팀 확정 완료!</div><p style="color:#fab005; font-size:1.2em; font-weight:bold;">➡️ 다음 {st.session_state.current_team_idx + 1}팀 발표를 시작해주세요.</p></div>', unsafe_allow_html=True)
        else:
            announcement_placeholder.markdown('<div class="announcement-fixed-box"><div class="announcement-title">🎉 모든 팀 구성이 완료되었습니다! 🎉</div><p style="color:#ccc; font-size:1.2em;">수고하셨습니다.</p></div>', unsafe_allow_html=True)

    c_btn = st.columns([1, 4])
    
    if c_btn[0].button("🔥 전체 팀 구성 생성"):
        slots = ["🍒", "🍋", "🔔", "⭐", "💎", "7️⃣", "🍀", "🍉"]
        for _ in range(15):
            s1, s2, s3 = random.choice(slots), random.choice(slots), random.choice(slots)
            announcement_placeholder.markdown(f'<div class="announcement-fixed-box"><div class="announcement-title">🔥 완벽한 밸런스를 계산 중입니다...</div><div class="slot-machine">{s1} {s2} {s3}</div></div>', unsafe_allow_html=True)
            time.sleep(0.08)
            
        st.session_state.teams_list = create_perfectly_balanced_teams(edited_df)
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
                    temp_name = edited_df.sample(1).iloc[0]['성명']
                    r_html = f'<div class="new-member-card"><div class="roulette-text">{temp_name}</div><div>추첨 중...</div></div>'
                    announcement_placeholder.markdown(f'<div class="announcement-fixed-box"><div class="announcement-title">📢 {idx+1}팀 멤버 추첨 중!</div><div style="display:flex; gap:20px;">{confirmed_cards}{r_html}</div></div>', unsafe_allow_html=True)
                    time.sleep(0.06)
                
                role_badge = '<span style="color:#fab005; font-size:1.2em;">👑 리더 (G1)</span>' if m_idx == 0 else f'<span style="color:#e0e0e0;">팀원 (G{int(target["그룹"])})</span>'
                
                confirmed_cards += f'<div class="new-member-card"><div style="margin-bottom:10px;">{role_badge}</div><div class="new-member-name">{target["성명"]}</div><div style="color:#fff; font-weight:bold; font-size:1.1em; margin-bottom:5px;">{int(target["학년"])}학년</div><div class="new-member-info">{target["학과"]}</div></div>'
                announcement_placeholder.markdown(f'<div class="announcement-fixed-box"><div class="announcement-title">📢 {idx+1}팀 멤버 추첨 중!</div><div style="display:flex; gap:20px;">{confirmed_cards}</div></div>', unsafe_allow_html=True)
                time.sleep(0.4)
            st.session_state.stage = "FINISHED"
            st.rerun()

        # 완료 화면
        if st.session_state.stage == "FINISHED":
            idx = st.session_state.current_team_idx
            members = st.session_state.teams_list[idx]
            
            cards = ""
            for i, m in enumerate(members):
                role_badge = '<span style="color:#fab005; font-size:1.2em;">👑 리더 (G1)</span>' if i == 0 else f'<span style="color:#e0e0e0;">팀원 (G{int(m["그룹"])})</span>'
                
                cards += f'<div class="new-member-card"><div style="margin-bottom:10px;">{role_badge}</div><div class="new-member-name">{m["성명"]}</div><div style="color:#fff; font-weight:bold; font-size:1.1em; margin-bottom:5px;">{int(m["학년"])}학년</div><div class="new-member-info">{m["학과"]}</div></div>'
                
            announcement_placeholder.markdown(f'<div class="announcement-fixed-box"><div class="announcement-title">✨ {idx+1}팀 구성 완료! ✨</div><div style="display:flex; gap:20px;">{cards}</div></div>', unsafe_allow_html=True)

        # 확정된 팀 명단 (최신순)
        if st.session_state.current_team_idx > 0:
            st.divider()
            st.subheader("📋 확정된 팀 명단 (최신순)")
            t_cols = st.columns(3)
            indices = list(range(st.session_state.current_team_idx))
            indices.reverse()
            for v_idx, r_idx in enumerate(indices):
                team = st.session_state.teams_list[r_idx]
                
                m_html = ""
                for i, m in enumerate(team):
                    bg_class = "leader-bg" if i == 0 else "normal-bg"
                    badge = '<span style="background:#fab005; color:white; padding:2px 6px; border-radius:4px; font-size:0.7em;">👑 G1 리더</span>' if i == 0 else f'<span style="background:#ced4da; color:white; padding:2px 6px; border-radius:4px; font-size:0.7em;">G{int(m["그룹"])}</span>'
                    
                    m_html += f'<div class="member-row {bg_class}"><div><b style="font-size:1.1em;">{m["성명"]}</b> {badge}</div><div style="font-size:0.85em; color:gray;">{int(m["학년"])}학년 | {m["학과"]}</div></div>'
                
                t_cols[v_idx % 3].markdown(f'<div class="team-card"><div class="team-title">TEAM {r_idx+1}</div>{m_html}</div>', unsafe_allow_html=True)
