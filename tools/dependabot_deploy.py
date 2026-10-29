"""Generate the fixed Windows Dependabot installation command; contains no secrets."""

import hashlib
import http.server
from pathlib import Path
import time

REVISION = "7da47aef53b0cfda7dda446dbb633d4317a28e73"
FILES = {
    "SKILL.md": "85179928b0838c542078747ed9f749209fa656590df593abeb9853ee43426edf",
    "references/dependabot-yml-reference.md": "c3b101d7e200a215211c9e23157ddfb1c051e437815b4d5a3d9bc13e504d6ed6",
    "references/example-configs.md": "35375699cfbaa372b68a232a2704f88a190e1267f937e1f1921e8d83c97485ca",
    "references/pr-commands.md": "471a786456c798364d13c0da554c12c712c581986b7f4a1de95d8b3638fd21cb",
}


TRANSFER_ORIGIN = 'http://100.123.213.15:49218'


def windows_installer(root=None):
    root = Path(root) if root else Path(__file__).resolve().parents[1]
    for name, digest in FILES.items():
        if hashlib.sha256((root / "skills/dependabot" / name).read_bytes()).hexdigest() != digest:
            raise ValueError("Dependabot source changed; review deployment manifest")
    manifest = ";".join("'" + name + "'='" + digest + "'" for name, digest in FILES.items())
    # No arbitrary command, source URL, destination, or account can be supplied.
    script = """& {
$ErrorActionPreference='Stop'
if($env:COMPUTERNAME -ine 'win-srv-01' -or $env:USERNAME -ine 'Administrator'){throw 'Unexpected machine or account'}
$files=@{MANIFEST}
$parent=Join-Path $env:USERPROFILE '.agents/skills'
foreach($p in @((Join-Path $env:USERPROFILE '.agents'),$parent)){if(Test-Path -LiteralPath $p){if((Get-Item -Force -LiteralPath $p).Attributes -band [IO.FileAttributes]::ReparsePoint){throw 'Linked parent refused'}}else{New-Item -ItemType Directory -Path $p|Out-Null}}
$target=Join-Path $parent 'dependabot'
function Verify($p){if(!(Test-Path -LiteralPath $p -PathType Container)){return $false};if((Get-Item -Force -LiteralPath $p).Attributes -band [IO.FileAttributes]::ReparsePoint){return $false};$all=@(Get-ChildItem -Force -Recurse -LiteralPath $p);if(@($all|Where-Object {$_.Attributes -band [IO.FileAttributes]::ReparsePoint}).Count){return $false};if(@($all|Where-Object {!$_.PSIsContainer}).Count -ne 4){return $false};foreach($n in $files.Keys){$f=Join-Path $p $n;if(!(Test-Path -LiteralPath $f -PathType Leaf)){return $false};if((Get-FileHash -Algorithm SHA256 -LiteralPath $f).Hash -ine $files[$n]){return $false}};return $true}
if(Test-Path -LiteralPath $target){if(!(Verify $target)){throw 'Existing skill differs; preserved'}}else{
$stage=Join-Path $parent ('.dependabot-'+[guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path (Join-Path $stage 'references')|Out-Null
foreach($n in $files.Keys){Invoke-WebRequest -UseBasicParsing -Uri ('TRANSFER_ORIGIN/'+$n) -OutFile (Join-Path $stage $n)}
if(!(Verify $stage)){throw 'Download verification failed; destination untouched'}
[IO.Directory]::Move($stage,$target)
}
if(!(Verify $target)){throw 'Installation verification failed'}
Write-Host ('DEPENDABOT VERIFIED: '+$target) -ForegroundColor Green
Write-Host '4 files; SHA-256 matches pinned source; globally available to Administrator.'
Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $target 'SKILL.md')|Format-List
}
""".replace("MANIFEST", manifest).replace("TRANSFER_ORIGIN", TRANSFER_ORIGIN)
    return script


def windows_command(root=None):
    digest = hashlib.sha256(windows_installer(root).encode('utf-8')).hexdigest()
    return ("& { $p=Join-Path $env:TEMP ('nebula-dependabot-'+[guid]::NewGuid()+'.ps1'); "
            "try { Invoke-WebRequest -UseBasicParsing -Uri '" + TRANSFER_ORIGIN + "/install.ps1' -OutFile $p -ErrorAction Stop; "
            "if((Get-FileHash -LiteralPath $p).Hash -ine '" + digest + "'){throw 'Installer hash mismatch'}; "
            "& ([scriptblock]::Create([IO.File]::ReadAllText($p))) } finally { if(Test-Path -LiteralPath $p){Remove-Item -LiteralPath $p} } }")


def serve():
    """Temporary Tailscale-only transfer: no repo listings, tokens, or secrets."""
    root = Path(__file__).resolve().parents[1]
    payloads = {'/install.ps1': windows_installer(root).encode('utf-8')}
    payloads.update({'/' + n: (root / 'skills/dependabot' / n).read_bytes() for n in FILES})

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            data = payloads.get(self.path) if self.client_address[0] == '100.121.209.21' else None
            if data is None:
                self.send_error(404)
                return
            self.send_response(200)
            self.send_header('Content-Type', 'application/octet-stream')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def log_message(self, *args):
            pass

    with http.server.HTTPServer(('100.123.213.15', 49218), Handler) as server:
        server.timeout = 1
        expires = time.monotonic() + 600
        print('Temporary skill transfer ready for win-srv-01 only; expires in 10 minutes.', flush=True)
        while time.monotonic() < expires:
            server.handle_request()


if __name__ == '__main__':
    serve()
