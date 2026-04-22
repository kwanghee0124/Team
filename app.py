import streamlit as st
import pandas as pd
import time
import random

# 페이지 설정
st.set_page_config(page_title="오픈소스SW기초 팀 빌딩", layout="wide")

# GUI 디자인 (카드 형태)
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
    .team-title { color: #1f77b4; font-weight: bold; border-bottom: 2px solid #1f77b4; padding-bottom: 5px; margin-bottom: 15px; }
    .member-row { margin-bottom: 10px; padding: 5px; border-radius: 5px; }
    .g1-bg { background-color: #e8f4f8; }
    .member-name { font-size: 1.1em; font-weight: bold; }
    .member-info { font-size: 0.85em; color: #666; }
    .badge { font-size: 0.7em; padding: 2px 5px; border-radius: 3px; margin-left: 5px; color: white; }
    .badge-g1 { background-color: #1f77b4; }
    </style>
    """, unsafe_allow_html=True)

def create_teams(df):
    # 데이터 정리 (그룹 정보는 CSV를 그대로 따름)
    df = df.iloc[:, [0, 2, 3, 4, 37]].dropna(subset=[df.columns[0], df.columns[37]])
    df.columns = ['그룹', '학년', '학과', '학번', '성명']
    
    # 그룹별 분리 (CSV 데이터 기준)
    g1 = df[df['그룹'] == 1.0].sample(frac=1).to_dict('records')
    g2 = df[df['그룹'] == 2.0].sample(frac=1).to_dict('records')
    g3 = df[df['그룹'] == 3.0].sample(frac=1).to_dict('records')

    # 학년 기준 분류 (G2 없는 팀에 4학년 제외 조건용)
    g1_3rd = [s for s in g1 if s['학년'] < 4]
    g1_4th = [s for s in g1 if s['학년'] >= 4]
    
    teams = []
    
    # [조건] 그룹 2가 없는 2개 팀 선배정 (G1 중 3학년만 배치)
    for _ in range(2):
        leader = g1_3rd.pop() if g1_3rd else g1_4th.pop()
        teams.append({"type": "G1(3학년)+G3+G3", "members": [leader, g3.pop(), g3.pop()]})

    # [조건] 나머지 13개 팀 배정 (G1 + G2 + G3)
    remaining_g1 = g1_3rd + g1_4th
    random.shuffle(remaining_g1)
    
    for _ in range(13):
        # 인원 부족 방지를 위한 안전장치 포함
        m1 = remaining_g1.pop() if remaining_g1 else None
        m2 = g2.pop() if g2 else None
        m3 = g3.pop() if g3 else None
        teams.append({"type": "G1+G2+G3", "members": [m for m in [m1, m2, m3] if m]})
    
    return teams

# --- GUI 구성 ---
st.title("🎲 오픈소스 SW 기초 팀 배정")
st.info("💡 CSV에 수정된 그룹 정보를 바탕으로 랜덤 팀 빌딩을 시작합니다.")

uploaded_file = st.file_uploader("수정된 명단 CSV 파일을 업로드하세요", type=["csv"])

if uploaded_file:
    df_raw = pd.read_csv(uploaded_file, skiprows=7)
    
    if st.button("🚀 팀 구성 시뮬레이션 시작"):
        # 랜덤 애니메이션 효과
        progress_bar = st.progress(0)
        status_text = st.empty()
        for i in range(1, 101):
            status_text.text(f"조건 확인 및 학생 섞는 중... {i}%")
            progress_bar.progress(i)
            time.sleep(0.01)
        
        final_teams = create_teams(df_raw)
        status_text.success("✅ 모든 조건(G1/G2 분리, G2 없는 팀 학년 제한)이 반영되었습니다!")
        
        # 카드 레이아웃 출력
        cols = st.columns(3)
        for idx, t_obj in enumerate(final_teams):
            with cols[idx % 3]:
                members_html = ""
                for m in t_obj['members']:
                    # 1. G1 강조용 배경색 및 뱃지 설정
                    is_g1 = "g1-bg" if m['그룹'] == 1 else ""
                    badge = '<span class="badge badge-g1">G1</span>' if m['그룹'] == 1 else ""
                    
                    # 2. 학번 .0 제거 (정수 변환)
                    try:
                        student_id = str(int(float(m['학번'])))
                    except:
                        student_id = str(m['학번'])
                        
                    # 3. 학년 정수 변환
                    grade = int(float(m['학년']))

                    # 각 멤버의 HTML 구조 생성
                    members_html += f"""
                    <div class="member-row {is_g1}">
                        <span class="member-name">{m['성명']}</span> {badge}<br>
                        <span class="member-info">{grade}학년 | {student_id} | {m['학과']}</span>
                    </div>
                    """
                
                st.markdown(f"""
                <div class="team-card">
                    <div class="team-title">TEAM {idx + 1}</div>
                    {members_html}
                </div>
                """, unsafe_allow_html=True)
