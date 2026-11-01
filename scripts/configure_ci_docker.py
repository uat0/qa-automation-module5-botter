"""Prepare a merged Docker mirror config for the disposable GitHub runner."""
from pathlib import Path
import json

source=Path('/etc/docker/daemon.json')
configuration=json.loads(source.read_text()) if source.exists() else {}
mirrors=configuration.setdefault('registry-mirrors',[])
mirror='https://dh-mirror.gitverse.ru'
if mirror not in mirrors:
    mirrors.append(mirror)
output=Path('results/docker-daemon.json')
output.parent.mkdir(parents=True,exist_ok=True)
output.write_text(json.dumps(configuration,indent=2)+'\n')
print('Prepared Docker Hub mirror configuration for CI')
