-- Investigation nestra-document-pack-400-20261110 attempt 1.
-- Run on the EXACT database used by the failed API request.
-- Read-only: no generation endpoint, stored procedure execution, transaction replay,
-- INSERT, UPDATE, DELETE, or template/customer document contents.
SET NOCOUNT ON;
SET LOCK_TIMEOUT 5000;
DECLARE @PackId int = 623, @ProposalId int = 11830;

SELECT CONVERT(nvarchar(128), SERVERPROPERTY('ServerName')) AS ServerName,
       DB_NAME() AS DatabaseName, SYSUTCDATETIME() AS ObservedAtUtc;

SELECT CASE WHEN EXISTS (SELECT 1 FROM dbo.Proposals WHERE ProposalID=@ProposalId)
            THEN 1 ELSE 0 END AS ProposalExists;

-- Preserve missing links and inactive/older versions so the exclusion is visible.
SELECT p.DocumentPackID, p.Active AS PackActive,
       RTRIM(p.Description) AS PackDescription,
       d.DocumentPackDocumentsID, d.DocumentTemplate, d.PageOrder,
       t.DocumentTemplateID, t.TemplateVersion, t.Active AS TemplateActive,
       t.DocumentType, RTRIM(ty.Description) AS TypeDescription,
       ty.FileExtension, t.DefaultTransmissionMethod,
       m.Description AS TransmissionDescription, m.FulfilmentApplication,
       CASE WHEN d.DocumentTemplate IS NULL THEN 'EMPTY PACK'
            WHEN t.DocumentTemplateID IS NULL THEN 'MISSING TEMPLATE'
            WHEN t.Active<>1 OR t.Active IS NULL THEN 'INACTIVE TEMPLATE'
            WHEN m.TransmissionMethod IS NULL THEN 'MISSING TRANSMISSION'
            WHEN m.FulfilmentApplication IS NULL THEN 'NULL FULFILMENT'
            WHEN m.FulfilmentApplication IN ('DPWS','NOTFULFILLED') THEN 'EXCLUDED FULFILMENT'
            ELSE 'ELIGIBLE FOR API INSERT' END AS ApiEligibility
FROM dbo.Document_Packs p
LEFT JOIN dbo.Document_Pack_Documents d ON d.DocumentPackID=p.DocumentPackID
LEFT JOIN dbo.Document_Templates t ON t.DocumentTemplate=d.DocumentTemplate
LEFT JOIN dbo.Document_Types ty ON ty.DocumentType=t.DocumentType
LEFT JOIN dbo.Document_Transmission_Methods m ON m.TransmissionMethod=t.DefaultTransmissionMethod
WHERE p.DocumentPackID=@PackId
ORDER BY d.DocumentPackDocumentsID,t.TemplateVersion;

-- Exact read-only projection of the API INSERT's joins and grouping.
-- Zero groups explains the reported exception (if proposal and active pack exist).
SELECT p.ProposalID, d.DocumentPackID, t.DefaultTransmissionMethod,
       ISNULL(d.OverridePrinterID,t.DefaultPrinterID) AS PrinterID,
       ISNULL(d.OverridePrinterTrayID,t.DefaultPrinterTrayID) AS PrinterTrayID,
       ISNULL(d.OverrideFormID,t.DefaultFormID) AS FormID,
       p.DocumentVersion, COUNT(*) AS MatchingTemplateRows
FROM dbo.Proposals p
CROSS JOIN dbo.Document_Pack_Documents d
INNER JOIN dbo.Document_Templates t ON d.DocumentTemplate=t.DocumentTemplate AND t.Active=1
INNER JOIN dbo.Document_Transmission_Methods m ON m.TransmissionMethod=t.DefaultTransmissionMethod
WHERE p.ProposalID=@ProposalId AND d.DocumentPackID=@PackId
  AND m.FulfilmentApplication NOT IN ('DPWS','NOTFULFILLED')
GROUP BY p.ProposalID,d.DocumentPackID,t.DefaultTransmissionMethod,
         ISNULL(d.OverridePrinterID,t.DefaultPrinterID),
         ISNULL(d.OverridePrinterTrayID,t.DefaultPrinterTrayID),
         ISNULL(d.OverrideFormID,t.DefaultFormID),p.DocumentVersion;

-- Metadata only. NULL can mean absent object or insufficient VIEW DEFINITION permission.
SELECT o.name,o.type_desc,OBJECT_DEFINITION(o.object_id) AS Definition
FROM sys.objects o
WHERE o.object_id IN (
  OBJECT_ID('dbo.trg_CreateExecutionRequestForDoc'),
  OBJECT_ID('dbo.sp_SF_RequestDoc'),
  OBJECT_ID('dbo.csp_EXS_ReserveDocumentsForProducing'),
  OBJECT_ID('dbo.csp_EXS_UnproducedDocuments'),
  OBJECT_ID('dbo.csp_EXS_GetDocumentTemplates'));
