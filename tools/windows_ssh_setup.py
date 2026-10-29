"""Fixed OpenSSH bootstrap for win-srv-01 via its verified KVM console."""
import hashlib
import http.server
from pathlib import Path
import re
import time

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = 'http://100.123.213.15:49219'


def installer():
    public = (ROOT / 'config/ssh/trigbotic-win-srv-01.pub').read_text().strip()
    if not re.fullmatch(r'ssh-ed25519 [A-Za-z0-9+/=]+ nebula-trigbotic-to-win-srv-01', public):
        raise ValueError('Unexpected dedicated public key')
    return r'''& {
$ErrorActionPreference='Stop'
if($env:COMPUTERNAME -ine 'win-srv-01' -or $env:USERNAME -ine 'Administrator'){throw 'Unexpected machine/account'}
$identity=[Security.Principal.WindowsIdentity]::GetCurrent()
if(!(New-Object Security.Principal.WindowsPrincipal($identity)).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)){throw 'Elevated PowerShell required'}
$sshd=Join-Path $env:WINDIR 'System32/OpenSSH/sshd.exe'
if(!(Test-Path -LiteralPath $sshd)){
 $result=Add-WindowsCapability -Online -Name 'OpenSSH.Server~~~~0.0.1.0'
 if($result.RestartNeeded){throw 'OpenSSH installation requires an operator-managed reboot'}
}
if(!(Test-Path -LiteralPath $sshd)){throw 'OpenSSH server missing'}
$ssh=Join-Path $env:ProgramData 'ssh'
if(Test-Path -LiteralPath $ssh){if((Get-Item -Force -LiteralPath $ssh).Attributes -band [IO.FileAttributes]::ReparsePoint){throw 'Linked SSH directory refused'}}
New-Item -ItemType Directory -Force -Path $ssh|Out-Null
$backup=Join-Path $ssh ('nebula-backup-'+(Get-Date -Format 'yyyyMMdd-HHmmss'))
New-Item -ItemType Directory -Path $backup|Out-Null
Get-Service sshd|Select-Object Name,Status,StartType|Export-Clixml -LiteralPath (Join-Path $backup 'service.xml')
$rule=Get-NetFirewallRule -Name 'OpenSSH-Server-In-TCP' -ErrorAction SilentlyContinue
if($rule){
 $rule|Export-Clixml -LiteralPath (Join-Path $backup 'firewall-rule.xml')
 $rule|Get-NetFirewallAddressFilter|Export-Clixml -LiteralPath (Join-Path $backup 'firewall-addresses.xml')
 Set-NetFirewallRule -Name 'OpenSSH-Server-In-TCP' -Enabled True -Direction Inbound -Action Allow -Profile Any -LocalAddress '100.121.209.21' -RemoteAddress '100.123.213.15'
}else{
 New-NetFirewallRule -Name 'OpenSSH-Server-In-TCP' -DisplayName 'OpenSSH from Nebula commander' -Enabled True -Direction Inbound -Action Allow -Protocol TCP -LocalPort 22 -LocalAddress '100.121.209.21' -RemoteAddress '100.123.213.15' -Profile Any|Out-Null
}
Set-Service sshd -StartupType Automatic
Start-Service sshd
& $sshd -t
if($LASTEXITCODE){throw 'Existing sshd configuration is invalid'}
$effective=& $sshd -T -C 'user=Administrator,host=win-srv-01,addr=100.123.213.15'
if($LASTEXITCODE -or !($effective -match '^authorizedkeysfile .*administrators_authorized_keys')){throw 'Administrator key path differs; inspect configuration before continuing'}
$keys=Join-Path $ssh 'administrators_authorized_keys'
if(Test-Path -LiteralPath $keys){
 if((Get-Item -Force -LiteralPath $keys).Attributes -band [IO.FileAttributes]::ReparsePoint){throw 'Linked authorized keys refused'}
 Copy-Item -LiteralPath $keys -Destination (Join-Path $backup 'administrators_authorized_keys')
 (Get-Acl -LiteralPath $keys)|Export-Clixml -LiteralPath (Join-Path $backup 'authorized-keys-acl.xml')
}
$line='from="100.123.213.15",no-agent-forwarding,no-port-forwarding,no-X11-forwarding PUBLIC_KEY'
$existing=if(Test-Path -LiteralPath $keys){[IO.File]::ReadAllText($keys)}else{''}
if(!($existing.Split([char]10).Trim() -contains $line)){
 [IO.File]::AppendAllText($keys,[Environment]::NewLine+$line+[Environment]::NewLine,(New-Object Text.UTF8Encoding($false)))
}
$acl=New-Object Security.AccessControl.FileSecurity
$admins=New-Object Security.Principal.SecurityIdentifier('S-1-5-32-544')
$system=New-Object Security.Principal.SecurityIdentifier('S-1-5-18')
$acl.SetOwner($admins)
$acl.SetAccessRuleProtection($true,$false)
foreach($sid in @($admins,$system)){$acl.AddAccessRule((New-Object Security.AccessControl.FileSystemAccessRule($sid,'FullControl','Allow')))}
Set-Acl -LiteralPath $keys -AclObject $acl
& $sshd -t
if($LASTEXITCODE){throw 'sshd validation failed'}
Write-Host 'SSH READY: Administrator; commander-only firewall and key source restriction' -ForegroundColor Green
Write-Host 'HOST ED25519 FINGERPRINT (verify from this pinned console):'
& (Join-Path $env:WINDIR 'System32/OpenSSH/ssh-keygen.exe') -lf (Join-Path $ssh 'ssh_host_ed25519_key.pub')
Get-Service sshd|Format-Table Name,Status,StartType
Write-Host ('Previous settings backed up at '+$backup)
}'''.replace('PUBLIC_KEY', public)


def windows_command():
    digest = hashlib.sha256(installer().encode()).hexdigest()
    return ("& { $p=Join-Path $env:TEMP ('nebula-ssh-'+[guid]::NewGuid()+'.ps1'); try { "
            "Invoke-WebRequest -UseBasicParsing -Uri '"+ORIGIN+"/setup.ps1' -OutFile $p -ErrorAction Stop; "
            "if((Get-FileHash -LiteralPath $p).Hash -ine '"+digest+"'){throw 'Installer hash mismatch'}; "
            "& ([scriptblock]::Create([IO.File]::ReadAllText($p))) } finally { if(Test-Path -LiteralPath $p){Remove-Item -LiteralPath $p} } }")


def serve():
    data = installer().encode()
    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            if self.client_address[0]!='100.121.209.21' or self.path!='/setup.ps1':
                self.send_error(404)
                return
            self.send_response(200)
            self.send_header('Content-Type','application/octet-stream')
            self.send_header('Content-Length',str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        def log_message(self,*args): pass
    with http.server.HTTPServer(('100.123.213.15',49219),Handler) as server:
        server.timeout=1
        expires=time.monotonic()+600
        print('Fixed SSH setup transfer ready for win-srv-01 only; expires in 10 minutes.',flush=True)
        while time.monotonic()<expires: server.handle_request()


if __name__=='__main__': serve()
