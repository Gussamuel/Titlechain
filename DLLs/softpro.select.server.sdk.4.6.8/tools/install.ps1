param (
    $InstallPath,
    $ToolsPath,
    $Package,
    $Project
)

$TargetsFile = 'SoftPro.Select.Sdk.targets'

# We have to use the Microsoft.Build assembly to get the project
Add-Type -AssemblyName 'Microsoft.Build, Version=4.0.0.0, Culture=Neutral, PublicKeyToken=b03f5f7f11d50a3a'

$MSBProject = [Microsoft.Build.Evaluation.ProjectCollection]::GlobalProjectCollection.GetLoadedProjects($Project.FullName) | 
    Select-Object -First 1

# If we have an existing import of this file, remove it
$ExistingImports = $MSBProject.Xml.Imports | 
    Where-Object { $_.Project -like "*\$TargetsFile" }

if ($ExistingImports) {
    $ExistingImports | 
        ForEach-Object {
            $MSBProject.Xml.RemoveChild($_) | Out-Null
        }
}

$Project.Save()