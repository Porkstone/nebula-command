# Result: nestra-document-pack-400-20261110 / attempt 1

Task: `nestra-document-pack-400-20261110`, attempt 1; dispatch `nestra-document-pack-400-20261110-a1`.
Worker: Trigbotic (`092fc721-316b-4b85-a39d-c99f1b65073f`). Investigation completed 2026-11-10, approximately 13:25 UTC.
Thread: <t3-thread://v2/092fc721-316b-4b85-a39d-c99f1b65073f/3ff6f605-60f1-4b72-9799-2e12933821ca>.
Repository: https://github.com/Market-Harborough-Building-Society/nestra-config-manager

## Outcome and confidence

**The API rejects a pack when its SQL INSERT SELECT yields zero document groups. The source filter is established; the specific configuration of pack #623 in the affected environment is not established.** No live request was replayed and no implementation or live correction was made.

The dropdown admits any active pack. Production requests additionally require at least one linked active template whose default transmission method exists and whose `FulfilmentApplication` is non-NULL and neither `DPWS` nor `NOTFULFILLED`. This mismatch is proven in source and explains how an offered selection can be rejected.

The message does **not** prove an unsupported file/template type. The API query does not inspect `DocumentType`, file extension, image contents, data source, or proposal-specific inclusion rules. These are later production concerns. A pack with an unsupported type and an otherwise eligible transmission can pass this API check and fail later.

Confidence: high in the source rejection mechanism and UI eligibility mismatch; unresolved in the incident's exact data cause. The deployed API commit, endpoint/database selection, pack membership, and template/transmission rows were not available. Do not assert that #623 is DPWS, inactive, empty, or misconfigured without the affected database evidence.

## Receipt and isolation

- Harness-managed branch: `investigate/document-pack-400`.
- Checkout: `C:\Users\Charl\.t3\worktrees\nestra-config-manager\investigate-document-pa-e9f2bf740aaaad77`.
- Requested handoff: same thread, `baseRef=origin/master`, `startFromOrigin=true`.
- Actual HEAD and fetched origin/master: `611bcd4065db6033f9afd456833383a76c1ab666`; no advancement from dispatch base.
- Checkout began clean. Only this report and its read-only SQL companion were added; no commit, application edit, PR, deployment, generation, merge, or ledger update.
- Original dirty root at `C:\Files\Development\Orange\Nestra\nestra-config-manager` was only read. Its unrelated modifications remain present.
- Applied fleet-work and get-table instructions. Existing table scripts were inspected and local SQL catalog metadata retrieved; existing scripts were not regenerated because this assignment prohibits application edits. No Convex source was touched. No plan was created.

## Incident evidence and trace discrepancy

The supplied PNG shows `/documents`, proposal 11830 and `Nestra - Direct Debit Mandate (#623)` with the reported 400 message. The screenshot's trace ID reads **`4000dc03-0000-6b00-b63f-84710c7967bb`**, while the assignment text gives **`4000dbf9-0000-6b00-b63f-84710c7967bb`**. Search both when correlating existing logs. The screenshot does not show which API environment/database is selected. A Vercel frontend URL alone does not identify its API or SQL database.

## UI to API to database

References below are relative to this checkout at the recorded HEAD.

1. `WebApp/src/components/Documents.tsx:255` captures `getApiBaseUrl()` when opening the modal; line 259 passes it to the modal. The modal uses this same URL for loading packs and submitting.
2. `WebApp/src/components/CreateProposalDocumentPackModal.tsx:45` installs an environment-change guard. At line 56 it keeps only `pack.active`; it does not fetch/check eligible membership. At line 78 it submits the selected numeric pack ID and proposal ID. The option value comes from `documentPackID`, not the description.
3. `Api/Data/DocumentPackRepository.cs:19` lists packs. Its optional recent-use filter does not assess production eligibility. `WebApp/src/lib/api.ts:1681` sends POST `/proposals/{proposalId}/document-packs` with `{documentPackId}`; `Api/Endpoints/ProposalDocumentPackEndpoints.cs:10` calls `RequestDocumentPackAsync`.
4. `Api/Data/ProposalRepository.cs:333` validates positive IDs. Lines 368-377 require the proposal to exist and the pack to be active. Their failures have different messages/statuses. Assuming the deployed code matches this source, the screenshot's specific message means those checks succeeded in that request's database.
5. Lines 340-362 INSERT one `Documents` row per transmission/printer/tray/form/version group. The join uses logical `DocumentTemplate`, all `Active=1` versions, and `DefaultTransmissionMethod`. Lines 353-357 require an active template, a matching transmission method, and `FulfilmentApplication NOT IN ('DPWS','NOTFULFILLED')`. SQL NULL semantics also exclude NULL fulfilment values. There is no explicit latest-version or document-type check.
6. Lines 379-382 inspect returned document IDs and throw the exact error if empty. Commit is only at line 384; disposal rolls back uncommitted work. `Api/Middleware/ExceptionHandlingMiddleware.cs:69` maps `ArgumentException` to 400 and line 50 includes the trace ID. A missing proposal would be 404; a missing/inactive pack would have another 400 message; SQL failures normally map to 500.

This is not a call to `csp_EXS_RequestDocument` or `sp_SF_RequestDoc`. The new API performs its own SQL. Its grouping resembles `Database/StoredProcedures/dbo.sp_SF_RequestDoc.sql:11`; the legacy procedure excludes DPWS at line 24, while this API also excludes NOTFULFILLED. Removing those filters without confirming the intended delivery channel is not a supported correction.

## Downstream production eligibility

Read-only inspection also used the canonical database and Execution Service source checkouts already on Trigbotic. These are corroborating local source, not proof of the affected deployment:

- Database source: `C:\Files\Development\Orange\Cognition\cognition-databases`, HEAD `28f790ea7830c57da2f8dc31bca615adcb747c97`.
- Execution Service: `C:\Files\Development\Orange\Cognition\cognition-exe`, HEAD `844428fa7ac438850d37c5489bfae1869324d8b2`.

Under the database checkout:

- `MHBSCognition/dbo/Tables/Documents.sql:563` defines `trg_CreateExecutionRequestForDoc`. On `Produced=0` transitions it queues a DOCUMENT task when the task/status configuration exists. Lines 618 and 638 exclude NOTFULFILLED. Lines 622 and 642 separate immediate/pending requests using `fn_PendingUntil`. Local `OBJECT_DEFINITION` retrieval corroborated this behavior. Thus arbitrary non-NULL fulfilment values passing the API do not guarantee successful production.
- `MHBSCognition/dbo/Stored Procedures/ExecutionService/csp_EXS_UnproducedDocuments.sql:37` creates detail records; line 51 requires active templates, line 63 handles transmission/hold mapping, and line 71 calls `fn_IncludeThisDocumentTemplate`. Form matching and existing-detail checks also apply. Line 77 returns `DocumentType` for the producer.
- `MHBSCognition/dbo/Stored Procedures/ExecutionService/csp_EXS_GetDocumentTemplates.sql:22` requires active templates for new detail selection; lines 25-27 apply fulfilment, form, and inclusion constraints. These cannot directly cause this earlier zero-group API exception because the API INSERT does not call them.

Under the Execution Service checkout, `Request.vb:1884` dispatches document creation to configured WORD/HTML/TEXT types and line 2040 reports an unknown type. `Request.vb:1494`, `:1526`, and `:1558` then select supported transmission behavior for those types. Numeric type IDs are loaded from system configuration, so they must not be guessed. None of this worker code emits the observed HTTP 400 message. Production versions and system-control mappings remain unverified.

## Actual diagnostics and tests

All SQL access used existing local Windows integrated authentication. No credentials were printed or copied. No customer names, bank details, document images, or customer document contents were queried.

- `sqlcmd -S localhost -E -d master`: verified local Cognition database inventory.
- Following get-table, `sys.tables/sys.columns/sys.types` verified definitions of Document_Packs, Document_Pack_Documents, Document_Templates, Document_Transmission_Methods, Document_Types, Documents, Proposals. The relevant joins/columns match the checked-in definitions; template identity and logical template/version distinction were confirmed.
- Targeted LEFT JOIN diagnostics for pack 623 in local `MHBSCognition`, `MHBSCognition_FF`, and `MHBSCognition_FF2` each returned **zero pack rows**. Proposal 11830 existence-only checks returned 1 in each. Do not interpret this as a diagnosis of the remote incident: a missing pack would produce a different message at this source version.
- A subsequent read-only, pack-ID-only search over all online local `MHBSCognition%` databases with a Document_Packs table also returned **no pack 623**. No other pack or customer records were scanned into output. `MHBSCognitionDeV2` has no dbo.Document_Packs and is not usable for this check.
- Local `MHBSCognition` has 186 packs, highest ID 618. Its transmission configuration includes methods 8/9/10 assigned to DPWS and 12/13/14 assigned to NOTFULFILLED. This demonstrates valid local channel categories, not #623's configuration.
- Sanitized connection metadata from the original root's development settings identifies DefaultConnection as localhost/MHBSCognition_FF2 and SqlServerAuthConnection as localhost/MHBSCognition; local Seq is localhost:5341. No affected-environment SQL connection or authenticated live API/log session was established. No unverified external host was probed and no credential was solicited.
- `dotnet test Tests/ProposalDocumentPacks/ProposalDocumentPacks.csproj --nologo --verbosity minimal`: **15 passed, 0 failed, 0 skipped**, test execution duration 4 seconds. Existing tests create unique `NestraDocPackTest_*` databases, use fake authorization and fixture triggers, and load no application settings. They test success/grouping/overrides, empty and excluded-only packs, invalid IDs, access/environment checks, transaction rollback, and returned document identity with triggers. They do not use production queue triggers or contact a producer.
- After testing, `SELECT COUNT(*) FROM sys.databases WHERE name LIKE 'NestraDocPackTest[_]%'` returned **0**.
- Pure `VALUES` SQL truth-table check: **8/8 passed**. Active EXS and another non-NULL nonexcluded app pass; inactive/missing templates, missing transmission, NULL fulfilment, DPWS and NOTFULFILLED fail. The OTHER case confirms that this predicate is an exclusion list, not proof of producer capability.
- The retained diagnostic SQL was executed against local MHBSCognition with `sqlcmd -b -i`: exit 0, no SQL errors. `git diff --check` passed; final worktree status contains only the new investigation directory.

## Recommended correction and exact next checks

First correlate the existing failed request in API logs using **both trace IDs** above. Record its request URL including any `/databases/...` prefix, API environment/deployed commit, and the effective SQL server/catalog. Do not resubmit the POST. The relevant logging originates in `ExceptionHandlingMiddleware.cs:34`; additional hosting/request logs or configuration may be needed to recover catalog identity.

Then run [document-pack-623-readonly.sql](nestra-document-pack-400-20261110-readonly.sql) on that exact catalog with an existing authorized connection. It returns only environment identity, proposal-existence flag, configuration rows, a SELECT-only projection of the API grouping, and object definitions. It never calls production stored procedures. It deliberately preserves inactive/missing/older template rows so the precise exclusion is visible.

Interpret and correct only after that evidence:

| Affected-database result | Recommended correction |
| --- | --- |
| Pack empty, missing linked logical template, or all versions inactive | Repair pack membership/activation through the established configuration process, with intended version confirmed. |
| Active templates route to DPWS | Confirm the intended DPWS/web-service signing or delivery workflow. Use that workflow, or deliberately configure an Execution Service-compatible pack if that is the requirement. Do not switch Bonafidee/channel settings merely to bypass this guard. |
| Active templates route to NOTFULFILLED (including hold/upload channels) | Treat as intentionally unfulfilled until business intent is confirmed. Use an appropriately configured generation pack/channel rather than removing the exclusion. |
| Missing transmission row or NULL fulfilment | Correct the transmission configuration for the intended producer; this is not a template-format diagnosis. |
| Eligible SELECT groups exist now | Compare configuration at incident time and deployed API SQL, effective server/catalog, and trace correlation. Current rows alone cannot explain historical failure. Check enabled Documents INSTEAD OF triggers if the deployed schema differs. |
| Pack/proposal absent | Wrong database, stale snapshot, changed configuration, or a different deployed code path; the observed source would emit an earlier different error. |

A separately authorized UX improvement should expose generation eligibility/reasons in the selector using the same server-side predicate; keep the API guard. A separately authorized capability review can validate downstream format/transmission combinations. Neither change was implemented here. There is currently insufficient evidence to recommend changing #623's DocumentType or deleting the DPWS/NOTFULFILLED exclusion.

Environment mismatch remains possible, not proven. `WebApp/src/lib/apiEndpoints.ts:6` maps local/dev/UAT/production independently of frontend hosting. UAT admins may select MHBSCognition or MHBSCognition_FF; `Api/Services/DatabaseRepositoryRegistration.cs:20` changes InitialCatalog after authorization. `ApiContext.tsx:26` and `:42` persist environment/database choices. Source uses the same captured base URL for list and POST and blocks changes while submitting, so a list-versus-POST environment race is not supported by the inspected code. The screenshot cannot resolve the selected environment.

## Remaining state

- Retain this checkout and the two `docs/investigations` artifacts for commander collection; no commit or PR.
- No investigation API/server, generator, SQL transaction, test runner, or disposable database remains running.
- The test build started an idle Roslyn compiler service, observed as dotnet PID 41484 (started 13:19:22 local clock); left intact as reusable build infrastructure to avoid disrupting shared tooling. Normal local SQL Server was already running and remains running.
- Existing application PR #121 and database PR #103 watches were not changed. No fleet ledger was altered and no follow-on work was started.
- Missing evidence: affected API URL/environment/catalog, deployed commit/schema, incident-time pack/template/transmission rows, trace-log correlation, and deployed downstream producer/system-control settings.


## Commander acceptance

Collected 2026-11-10T13:25:44.239390+00:00. Worker run 6 completed. Parent inspected the exact API predicate/error and retained read-only SQL, independently verified investigation-only worktree status and clean diff check. Bounded investigation accepted; affected-environment cause remains unresolved. Active execution reservation released; retain isolated checkout and both artifacts. No implementation, live correction or merge was performed.
