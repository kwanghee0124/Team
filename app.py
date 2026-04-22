import streamlit as st
import pandas as pd
import time
import random

st.set_page_config(page_title="오픈소스SW기초 팀 배정", layout="wide")

# CSS 스타일 (기존 스타일 유지 + 추가)
st.markdown("""
    <style>
    .team-card {
        background-color: #ffffff; border-radius: 12px; padding: 20px;
        margin-bottom: 20px; border: 1px solid #e1e4e8;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); animation: fadeIn 0.5s;
    }
    @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
    .team-title { color: #1f77b4; font-size: 1.3em; font-weight: bold; border-bottom: 2px solid #1f77b4; padding-bottom: 8px; margin-bottom: 15px; }
    .member-row { margin-bottom: 10px; padding: 8px; border-radius: 8px; }
    .g1-bg { background-color: #e8f4f8; border-left: 4px solid #1f77b4; }
    .member-name { font-size: 1.1em; font-weight: bold; color: #333; }
    .member-info { font-size: 0.85em; color: #666; }
    .badge { font-size: 0.7em; padding: 2px 6px; border-radius: 4px; margin-left: 5px; color: white; background-color: #1f77b4; }
    </style>
    """, unsafe_allow_html=True)

def create_teams(df_clean):
    g1 = df_clean[df_clean['그룹'] == 1.0].sample(frac=1).to_dict('records')
    g2 = df_clean[df_clean['그룹'] == 2.0].sample(frac=1).to_dict('records')
    g3 = df_clean[df_clean['그룹'] == 3.0].sample(frac=1).to_dict('records')

    g1_3rd = [s for s in g1 if float(s['학년']) < 4]
    g1_4th = [s for s in g1 if float(s['학년']) >= 4]
    
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

    # 1. 그룹별 학생 리스트 미리 보여주기
    st.subheader("👥 그룹별 학생 리스트")
    expander = st.expander("리스트 확인하기 (클릭)")
    with expander:
        c1, c2, c3 = st.columns(3)
        for g_num, col in zip([1, 2, 3], [c1, c2, c3]):
            group_data = df_clean[df_clean['그룹'] == float(g_num)]
            col.markdown(f"**그룹 {g_num} ({len(group_data)}명)**")
            col.dataframe(group_data[['성명', '학년', '학번']], hide_index=True)

    if st.button("🚀 팀 추첨 시작"):
        final_teams = create_teams(df_clean)
        
        st.divider()
        st.subheader("🎊 팀 배정 결과")
        
        # 2. 한 팀씩 등장하는 애니메이션 효과
        container = st.container()
        # 3열 구성을 미리 준비
        rows = [st.columns(3) for _ in range(5)] # 15팀이므로 5줄
        
        for idx, team_members in enumerate(final_teams):
            row_idx = idx // 3
            col_idx = idx % 3
            
            # 발표 전 "두구두구" 효과 (짧게 회전하는 느낌)
            with rows[row_idx][col_idx]:
                placeholder = st.empty()
                for _ in range(5): # 5번 빠르게 이름 섞기
                    temp_name = random.choice(df_clean['성명'].tolist())
                    placeholder.markdown(f"""<div class="team-card"><h4>TEAM {idx+1}</h4><p>추첨 중... {temp_name}</p></div>""", unsafe_allow_html=True)
                    time.sleep(0.1)
                
                # 최종 팀원 HTML 생성
                members_html = ""
                for m in team_members:
                    is_g1 = "g1-bg" if float(m['그룹']) == 1.0 else ""
                    badge = '<span class="badge">G1</span>' if float(m['그룹']) == 1.0 else ""
                    sid = str(int(float(m['학번'])))
                    grade = str(int(float(m['학년'])))
                    members_html += f'<div class="member-row {is_g1}"><span class="member-name">{m["성명"]}</span>{badge}<br><span class="member-info">{grade}학년 | {sid} | {m["학과"]}</span></div>'
                
                # 최종 확정 결과 출력
                placeholder.markdown(f'<div class="team-card"><div class="team-title">TEAM {idx + 1}</div>{members_html}</div>', unsafe_allow_html=True)
                time.sleep(0.5) # 한 팀 나오고 다음 팀까지 대기 시간

        st.balloons() # 모든 팀 발표 후 풍선 효과
