import streamlit as st
import pandas as pd
import time
import random

# 1. 페이지 설정 및 디자인(CSS) 정의
st.set_page_config(page_title="오픈소스SW기초 팀 배정", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .team-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        border: 1px solid #e1e4e8;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        min-height: 250px;
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
        margin-bottom: 12px; 
        padding: 8px; 
        border-radius: 8px;
        line-height: 1.4;
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
        vertical-align: middle;
    }
    .badge-g1 { background-color: #1f77b4; }
    </style>
    """, unsafe_allow_html=True)

def create_teams(df):
    # 데이터 전처리 (CSV 헤더 위치에 맞춰 컬럼 추출)
    # 그룹(0), 학년(2), 학과(3), 학번(4), 성명(37)
    df_clean = df.iloc[:, [0, 2, 3, 4, 37]].dropna(subset=[df.columns[0], df.columns[37]])
    df_clean.columns = ['그룹', '학년', '학과', '학번', '성명']
    
    # 그룹별 분리 (사용자가 수정한 CSV 그룹 정보 그대로 사용)
    g1 = df_clean[df_clean['그룹'] == 1.0].sample(frac=1).to_dict('records')
    g2 = df_clean[df_clean['그룹'] == 2.0].sample(frac=1).to_dict('records')
    g3 = df_clean[df_clean['그룹'] == 3.0].sample(frac=1).to_dict('records')

    # G1 내에서 학년 기준 분류 (G2 없는 팀용)
    g1_3rd = [s for s in g1 if float(s['학년']) < 4]
    g1_4th = [s for s in g1 if float(s['학년']) >= 4]
    
    teams = []
    
    # [규칙 1] G2가 없는 2개 팀 선배정 (G1 중 3학년만 배치)
    for _ in range(2):
        leader = g1_3rd.pop() if g1_3rd else g1_4th.pop()
        teams.append([leader, g3.pop(), g3.pop()])

    # [규칙 2] 나머지 13개 팀 배정 (G1 + G2 + G3)
    remaining_g1 = g1_3rd + g1_4th
    random.shuffle(remaining_g1)
    
    for _ in range(13):
        m1 = remaining_g1.pop() if remaining_g1 else None
        m2 = g2.pop() if g2 else None
        m3 = g3.pop() if g3 else None
        team = [m for m in [m1, m2, m3] if m]
        teams.append(team)
    
    return teams

# 2. GUI 상단 구성
st.title("🎲 오픈소스SW기초 팀 배정 시스템")
st.write("실시간 랜덤 배정입니다.")

uploaded_file = st.file_uploader("CSV 파일을 업로드하세요", type=["csv"])

if uploaded_file:
    # 데이터 로드 (파일 상단 7줄 무시)
    df_raw = pd.read_csv(uploaded_file, skiprows=7)
    
    if st.button("🚀 랜덤 팀 구성 및 시뮬레이션 시작"):
        # 애니메이션 효과
        progress_bar = st.progress(0)
        status_text = st.empty()
        for i in range(1, 101):
            status_text.text(f"알고리즘 연산 중... {i}%")
            progress_bar.progress(i)
            time.sleep(0.01)
        
        final_teams = create_teams(df_raw)
        status_text.success("✅ 팀 배정이 완료되었습니다!")
        
        # 3. 카드 레이아웃 출력 (가장 중요한 부분)
        cols = st.columns(3)
        for idx, team_members in enumerate(final_teams):
            with cols[idx % 3]:
                members_html = ""
                for m in team_members:
                    # G1 강조 여부 및 뱃지
                    is_g1_class = "g1-bg" if float(m['그룹']) == 1.0 else ""
                    badge_html = '<span class="badge badge-g1">G1</span>' if float(m['그룹']) == 1.0 else ""
                    
                    # 학번/학년 포맷팅 (.0 제거)
                    try:
                        sid = str(int(float(m['학번'])))
                        grade = str(int(float(m['학년'])))
                    except:
                        sid = str(m['학번'])
                        grade = str(m['학년'])
                    
                    # 개별 멤버 HTML 생성
                    members_html += f"""
                    <div class="member-row {is_g1_class}">
                        <span class="member-name">{m['성명']}</span> {badge_html}<br>
                        <span class="member-info">{grade}학년 | {sid} | {m['학과']}</span>
                    </div>
                    """
                
                # 팀 카드 렌더링 (unsafe_allow_html=True 필수)
                st.markdown(f"""
                <div class="team-card">
                    <div class="team-title">TEAM {idx + 1}</div>
                    {members_html}
                </div>
                """, unsafe_allow_html=True)

        # 결과 다운로드 옵션
        all_data = []
        for i, t in enumerate(final_teams):
            for m in t:
                all_data.append({"팀": f"{i+1}팀", "성명": m['성명'], "학번": m['학번'], "학년": m['학년'], "그룹": m['그룹']})
        
        df_res = pd.DataFrame(all_data)
        csv_data = df_res.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 전체 결과 CSV 다운로드", csv_data, "team_results.csv", "text/csv")
