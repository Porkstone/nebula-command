#Requires -Version 5.1
<#
.SYNOPSIS
Reads local Windows hardware and OS facts as JSON. Makes no configuration changes.
#>
[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$osInfo = Get-CimInstance -ClassName Win32_OperatingSystem
$systemInfo = Get-CimInstance -ClassName Win32_ComputerSystem
$cpuInfo = @(Get-CimInstance -ClassName Win32_Processor | ForEach-Object {
    [ordered]@{ name = $_.Name; cores = $_.NumberOfCores; logical_processors = $_.NumberOfLogicalProcessors }
})
$gpuInfo = @(Get-CimInstance -ClassName Win32_VideoController | ForEach-Object { $_.Name })
$diskInfo = @(Get-CimInstance -ClassName Win32_LogicalDisk -Filter 'DriveType=3' | ForEach-Object {
    [ordered]@{ drive = $_.DeviceID; size_bytes = $_.Size; free_bytes = $_.FreeSpace }
})

[ordered]@{
    collected_at_utc = [DateTime]::UtcNow.ToString('o')
    hostname = [System.Net.Dns]::GetHostName()
    os = [ordered]@{ name = $osInfo.Caption; version = $osInfo.Version; architecture = $osInfo.OSArchitecture }
    memory_bytes = $systemInfo.TotalPhysicalMemory
    cpus = $cpuInfo
    gpus = $gpuInfo
    fixed_disks = $diskInfo
} | ConvertTo-Json -Depth 6
