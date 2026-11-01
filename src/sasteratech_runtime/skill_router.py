import json,re
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class SkillMatch:
    skill_id:str
    score:float
    reasons:tuple[str,...]

class SkillRouter:
    def __init__(self,skills_root):
        self.skills=[]
        for p in sorted(Path(skills_root).glob('*/skill.json')):
            self.skills.append(json.loads(p.read_text(encoding='utf-8')))

    @staticmethod
    def _tokens(text):
        return set(re.findall(r'[a-z0-9]+',text.lower()))

    def _score(self,skill,query):
        q=query.lower(); qt=self._tokens(q)
        negatives=skill.get('negative_triggers',[])
        for neg in negatives:
            nt=self._tokens(neg)
            if nt and nt.issubset(qt):
                return -100.0,(f'negative:{neg}',)
        score=0.0; reasons=[]
        for trig in skill.get('positive_triggers',[]):
            tt=self._tokens(trig)
            if trig.lower() in q:
                score+=5.0; reasons.append(f'exact:{trig}')
            elif tt:
                overlap=len(qt & tt)/len(tt)
                if overlap>=0.5:
                    score+=2.0*overlap; reasons.append(f'overlap:{trig}:{overlap:.2f}')
        # Stable semantic anchors from purpose/id, not model inference.
        anchors=self._tokens(skill.get('purpose','')) | self._tokens(skill.get('id','').replace('.',' '))
        anchor_hits=qt & anchors
        score += min(3.0,0.5*len(anchor_hits))
        if anchor_hits: reasons.append('anchors:'+','.join(sorted(anchor_hits)))
        return score,tuple(reasons)

    def rank(self,query):
        matches=[]
        for s in self.skills:
            score,reasons=self._score(s,query)
            if score>0:
                matches.append(SkillMatch(s['id'],score,reasons))
        return sorted(matches,key=lambda x:(-x.score,x.skill_id))

    def select(self,query,min_score=1.0):
        ranked=self.rank(query)
        if not ranked or ranked[0].score<min_score: return None
        return ranked[0].skill_id

    def trajectory(self,query):
        selected=self.select(query)
        return [] if selected is None else [selected]
