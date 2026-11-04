$docxPath = "C:\Users\rohit\OneDrive\Desktop\web tech pro\Vehicle_Service_Management_System_Project_Report.docx"
$pdfPath = "C:\Users\rohit\OneDrive\Desktop\web tech pro\Vehicle_Service_Management_System_Project_Report.pdf"

try {
    Write-Host "Initializing Microsoft Word..."
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = [Microsoft.Office.Interop.Word.WdAlertLevel]::wdAlertsNone

    Write-Host "Opening document: $docxPath"
    $doc = $word.Documents.Open($docxPath, $false, $true)

    Write-Host "Exporting to PDF: $pdfPath"
    # 17 is wdExportFormatPDF
    $doc.ExportAsFixedFormat($pdfPath, 17)

    $doc.Close([Microsoft.Office.Interop.Word.WdSaveOptions]::wdDoNotSaveChanges)
    $word.Quit()
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($word) | Out-Null
    [System.GC]::Collect()
    [System.GC]::WaitForPendingFinalizers()

    Write-Host "PDF generated successfully!"
} catch {
    Write-Error $_.Exception.Message
}
