"""교재의 로컬 파일, 헤딩, Python 파서와 정답 분석기를 검증합니다."""
from pathlib import Path
import ast
import csv
import json
import math
import re
import runpy
import tempfile
import zipfile
from urllib.parse import unquote

ROOT=Path(__file__).resolve().parents[1]
errors=[];checks=0
def check(value,message):
    global checks
    checks+=1
    if not value:errors.append(message)

def main():
    config=ROOT/'repository.json'
    repo=json.loads(config.read_text(encoding='utf-8')) if config.exists() else None
    for file in ROOT.rglob('*.md'):
        text=file.read_text(encoding='utf-8')
        # Fenced code may contain C preprocessor directives beginning with #.
        prose=re.sub(r'```.*?```','',text,flags=re.S)
        if file.parent.name=='pages':
            check(not re.search(r'^# ',prose,re.M),f'본문 H1: {file.name}')
            check(bool(re.search(r'!\[[^\]]+\]\(',prose)),f'이미지 없음: {file.name}')
        check(text.count('```')%2==0,f'코드 울타리 불균형: {file}')
        for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',prose):
            if repo and target.startswith(repo['repo']+'/blob/'+repo['branch']+'/'):
                rel=unquote(target.split('/blob/'+repo['branch']+'/',1)[1]);path=ROOT/rel
            elif target.startswith(('http:','https:','#','mailto:')):
                continue
            else:path=file.parent/unquote(target.split('#')[0])
            check(path.exists(),f'링크 대상 없음: {file.relative_to(ROOT)} → {target}')
    for file in ROOT.rglob('*.py'):
        try:tree=ast.parse(file.read_text(encoding='utf-8'))
        except SyntaxError as e:errors.append(f'{file}: {e}');continue
        checks_before=len(errors)
        if file.name=='read_sensor.py':
            # Run the actual parser without importing serial or opening a port.
            nodes=[n for n in tree.body if (isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='COLUMNS' for t in n.targets)) or (isinstance(n,ast.FunctionDef) and n.name=='parse_line')]
            scope={'math':math};exec(compile(ast.Module(body=nodes,type_ignores=[]),str(file),'exec'),scope)
            count=len(scope['COLUMNS']);parse=scope['parse_line']
            check(parse(','.join(['1.5']*count))==[1.5]*count,f'정상 파싱: {file}')
            for token in ['ERROR','TIMEOUT','nan','inf','']:
                check(parse(','.join([token]*count)) is None,f'오류값 처리: {file}, {token}')
            check(parse(','.join(['1']*(count+1))) is None,f'열 수 처리: {file}')
        if file.name=='analyze.py':
            namespace=runpy.run_path(str(file));func=namespace['summarize']
            id=file.parent.name;sample=ROOT/'samples'/(id+'.csv')
            result=func(sample)
            check(result is not None and result[0]==2,f'모의 데이터 분석: {id}')
            with tempfile.TemporaryDirectory() as tmp:
                p=Path(tmp)/'empty.csv';header=sample.read_text(encoding='utf-8').splitlines()[0]
                p.write_text(header+'\n0,ERROR\n1,nan\n',encoding='utf-8')
                check(func(p) is None,f'유효값 없는 분석: {id}')
    chapters=list((ROOT/'pages').glob('*.md'))
    check(len(chapters)==30,f'본문 개수: {len(chapters)}')
    decks=list((ROOT/'slides').glob('*.pptx'))
    check(len(decks)==30,f'PPT 개수: {len(decks)}')
    for deck in decks:
        with zipfile.ZipFile(deck) as z:
            check(z.testzip() is None,f'PPT ZIP 손상: {deck.name}')
            slides=[n for n in z.namelist() if re.fullmatch(r'ppt/slides/slide\d+\.xml',n)]
            check(len(slides)==4,f'PPT 슬라이드 수: {deck.name}')
    check(len(list((ROOT/'worksheets').glob('session-*.md')))==30,'30차시 활동지 수')
    report={'checks':checks,'passed':not errors,'errors':errors,'scope':'Local links, Markdown, Python parser/analysis behavior, PPT package counts. No board compilation, hardware or live WikiDocs verification.'}
    (ROOT/'validation-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
    raise SystemExit(0 if not errors else 1)

if __name__=='__main__':main()
