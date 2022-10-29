$pythonFile = $PSCommandPath.replace(".ps1", ".py")

$pythonEnv = $PSCommandPath.Replace(".ps1", "")
$EnvActPath = "$pythonEnv\Scripts\activate.ps1"
$pythonPath = "$pythonEnv\Scripts\python.exe"

write-host "Running Venv from $EnvActPath"

If(Test-Path -Path $pythonFile -PathType Leaf){
    If(Test-Path -Path $EnvActPath -PathType Leaf){
        & $pythonPath $pythonFile
    } 
    else {
        throw "Unable to find Virtual Env. $EnvActPath"
    }
} 
else {
    throw "Unable to find py File. $pythonFile"
}
