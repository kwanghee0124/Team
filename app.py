def create_strictly_balanced_teams(df_clean):
    # 1. 그룹별/성별/학년별 데이터 정밀 분리
    def get_refined_split(group_num):
        group_data = [x for x in df_clean.to_dict('records') if x['그룹'] == float(group_num)]
        if group_num == 1:
            # G1 내에서 저학년(1~3학년)과 고학년(4학년 이상) 분리
            low = [x for x in group_data if int(float(x['학년'])) < 4]
            high = [x for x in group_data if int(float(x['학년'])) >= 4]
            random.shuffle(low); random.shuffle(high)
            return low, high
        
        m = [x for x in group_data if x['성별'] == '남']
        f = [x for x in group_data if x['성별'] == '여']
        random.shuffle(m); random.shuffle(f)
        return m, f

    g1_low, g1_high = get_refined_split(1)
    g2_m, g2_f = get_refined_split(2)
    g3_m, g3_f = get_refined_split(3)

    num_teams = 15
    teams = [[] for _ in range(num_teams)]

    # [규칙 1] G1과 G2는 절대 같은 팀 불가
    # [규칙 2] G3가 2명 들어가는 팀(G2 없는 팀)의 G1은 반드시 저학년이어야 함
    
    # 15개 팀 중 G2가 배치될 팀 수 계산 (G2 전체 인원수)
    num_g2 = len(g2_m) + len(g2_f)
    # G2가 들어가지 못하는 팀 수 (G3가 2명 들어갈 팀)
    num_no_g2_teams = num_teams - num_g2 # 예: 15 - 13 = 2팀
    
    # 리더 배치 시나리오
    # A. G2가 없는 팀 (G1 저학년 + G3 + G3)
    for i in range(num_no_g2_teams):
        if g1_low:
            teams[i].append(g1_low.pop(0))
        elif g1_high: # 저학년이 부족할 경우에만 어쩔 수 없이 고학년 (거의 발생 안 함)
            teams[i].append(g1_high.pop(0))
            
    # B. G2가 있는 팀 (G1 + G2 + G3)
    for i in range(num_no_g2_teams, num_teams):
        # G1 남은 인원 (고학년 우선 소진하여 저학년을 보호하거나, 남은 대로 배치)
        if g1_high:
            teams[i].append(g1_high.pop(0))
        elif g1_low:
            teams[i].append(g1_low.pop(0))
            
        # G2 한 명씩 배치 (G1과 같은 팀)
        if g2_f: teams[i].append(g2_f.pop(0))
        elif g2_m: teams[i].append(g2_m.pop(0))

    # [규칙 3] 성별 균형 및 G3 채우기 (팀당 여학생 최대 2명)
    # 아직 배치되지 않은 모든 여학생/남학생 풀 구성
    assigned_ids = [m['학번'] for t in teams for m in t]
    rem_f = [x for x in (g3_f + g2_f + g1_low + g1_high) if x['학번'] not in assigned_ids and x['성별'] == '여']
    rem_m = [x for x in (g3_m + g2_m + g1_low + g1_high) if x['학번'] not in assigned_ids and x['성별'] == '남']
    random.shuffle(rem_f); random.shuffle(rem_m)

    for i in range(num_teams):
        while len(teams[i]) < 3:
            current_f_count = len([m for m in teams[i] if m['성별'] == '여'])
            
            # G3 우선적으로 채우기 (특히 G2 없는 팀은 G3 2명 필수)
            # 여기서는 남은 인원 전체(rem_f, rem_m)에서 성별 고려하여 pop
            if current_f_count < 2 and rem_f:
                teams[i].append(rem_f.pop(0))
            elif rem_m:
                teams[i].append(rem_m.pop(0))
            elif rem_f: # 남학생이 아예 없으면 어쩔 수 없이 여학생
                teams[i].append(rem_f.pop(0))
            else:
                break

    random.shuffle(teams) # 팀 순서 섞기
    return teams
