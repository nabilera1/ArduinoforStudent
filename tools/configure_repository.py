"""GitHub 주소가 확정되면 일반 파일 링크를 외부 GitHub 링크로 바꿉니다."""
import argparse
import json
import re
from pathlib import Path
from urllib.parse import quote, urlparse

ROOT = Path(__file__).resolve().parents[1]

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--repo', required=True)
    p.add_argument('--branch', default='main')
    args = p.parse_args()
    repo = args.repo.rstrip('/').removesuffix('.git')
    parsed = urlparse(repo)
    if parsed.scheme != 'https' or parsed.netloc != 'github.com' or len(parsed.path.strip('/').split('/')) != 2:
        raise SystemExit('https://github.com/소유자/저장소 형식으로 입력하세요.')
    config_path = ROOT / 'repository.json'
    old = json.loads(config_path.read_text(encoding='utf-8')) if config_path.exists() else None
    for file in ROOT.rglob('*.md'):
        content = file.read_text(encoding='utf-8')
        if old:
            content = content.replace(old['repo']+'/blob/'+old['branch']+'/', repo+'/blob/'+args.branch+'/')
        def convert(match):
            label, link = match.groups()
            if link.startswith(('https:', 'http:', '#')):
                return match.group(0)
            target = (file.parent / link).resolve()
            if target.suffix.lower() not in {'.ino','.py','.pptx','.zip','.csv'}:
                return match.group(0)
            try:
                rel=target.relative_to(ROOT).as_posix()
            except ValueError:
                return match.group(0)
            # GitHub file view supports reviewing source and downloading the raw file.
            url=repo+'/blob/'+quote(args.branch,safe='')+'/'+quote(rel,safe='/')
            return f'[{label}]({url})'
        content=re.sub(r'(?<!!)\[([^\]]+)\]\(([^)]+)\)',convert,content)
        file.write_text(content,encoding='utf-8')
    config_path.write_text(json.dumps({'repo':repo,'branch':args.branch},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Updated GitHub source/download links. Verify the branch and public access before publishing.')

if __name__=='__main__':
    main()
