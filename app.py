import streamlit as st
import pandas as pd
import time
import random

# 1. 페이지 설정 및 디자인(CSS) 정의
st.set_page_config(page_title="오픈소스SW기초 팀 배정", layout="wide")

# CSS 정의
st.markdown("""
    <style>
    .team-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        border: 1px solid #e1e4e8;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .team-title { 
        color: #1f77b4; 
        font-size: 1.3em;
        font-weight: bold; 
        border-bottom: 2px solid #1f77b4; 
        padding-bottom: 8px; 
        margin-bottom: 15px; 
    }
    .member-row { 
        margin-bottom: 10px; 
        padding: 8px; 
        border-radius: 8px;
    }
    .g1-bg { background-color: #e8f4f8; border-left: 4px solid #1f77b4; }
    .member-name { font-size: 1.1em; font-weight: bold; color: #333; }
    .member-info { font-size: 0.85em; color: #666; }
    .badge { 
        font-size: 0.7em; 
        padding: 2px 6px; 
        border-radius: 4px; 
        margin-left: 5px; 
        color: white; 
        background-color: #1f77b4;
    }
    </style>
    """, unsafe_allow_html=True)

def create_teams(df):
    # 데이터 전처리
    df_clean = df.iloc[:, [0, 2, 3, 4, 37]].dropna(subset=[df.columns[0], df.columns[37]])
    df_clean.columns = ['그룹', '학년', '학과', '학번', '성명']
    
    g1 = df_clean[df_clean['그룹'] == 1.0].sample(frac=1).to_dict('records')
    g2 = df_clean[df_clean['그룹'] == 2.0].sample(frac=1).to_dict('records')
    g3 = df_clean[df_clean['그룹'] == 3.0].sample(frac=1).to_dict('records')

    g1_3rd = [s for s in g1 if float(s['학년']) < 4]
    g1_4th = [s for s in g1 if float(s['학년']) >= 4]
    
    teams = []
    # G2 없는 2개 팀 (G1 3학년만)
    for _ in range(2):
        leader = g1_3rd.pop() if g1_3rd else g1_4th.pop()
        teams.append([leader, g3.pop(), g3.pop()])

    # 나머지 13개 팀
    remaining_g1 = g1_3rd + g1_4th
    random.shuffle(remaining_g1)
    for _ in range(13):
        m1 = remaining_g1.pop() if remaining_g1 else None
        m2 = g2.pop() if g2 else None
        m3 = g3.pop() if g3 else None
        teams.append([m for m in [m1, m2, m3] if m])
    
    return teams

st.title("🎲 오픈소스 SW 기초 팀 배정 시스템")

uploaded_file = st.file_uploader("CSV 업로드", type=["csv"])

if uploaded_file:
    df_raw = pd.read_csv(uploaded_file, skiprows=7)
    
    if st.button("🚀 랜덤 팀 구성 시작"):
        with st.spinner('팀을 섞는 중입니다...'):
            time.sleep(1) # 시뮬레이션 느낌
            final_teams = create_teams(df_raw)
        
        st.success("✅ 배정 완료!")
        
        # 출력 부분
        cols = st.columns(3)
        for idx, team_members in enumerate(final_teams):
            with cols[idx % 3]:
                # 멤버 HTML 생성
                members_html = ""
                for m in team_members:
                    is_g1 = "g1-bg" if float(m['그룹']) == 1.0 else ""
                    badge = '<span class="badge">G1</span>' if float(m['그룹']) == 1.0 else ""
                    
                    try:
                        sid = str(int(float(m['학번'])))
                        grade = str(int(float(m['학년'])))
                    except:
                        sid = str(m['학번'])
                        grade = str(m['학년'])
                    
                    # f-string 내부 줄바꿈 제거 (안정성 확보)
                    row = f'<div class="member-row {is_g1}"><span class="member-name">{m["성명"]}</span>{badge}<br><span class="member-info">{grade}학년 | {sid} | {m["학과"]}</span></div>'
                    members_html += row
                
                # 최종 카드 렌더링
                card_html = f'<div class="team-card"><div class="team-title">TEAM {idx + 1}</div>{members_html}</div>'
                st.markdown(card_html, unsafe_allow_html=True)
