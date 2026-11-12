# Best Practice Analyzer

Rules and tooling for checking `CDPR_Health_Hub.SemanticModel` against
Microsoft's Best Practice Rules for tabular models.

Current state: **0 violations**, Tabular Editor exits 0.

## Rules file

`BPARules.json` holds **68 rules**: Microsoft's 71, minus the 3 listed under
[Removed rules](#removed-rules).

- Source: <https://raw.githubusercontent.com/microsoft/Analysis-Services/master/BestPracticeRules/BPARules.json>
- Downloaded: 2026-11-06, 71 rules, 55 920 bytes,
  SHA-256 `ddb9cff4c2a0611a6467e2559d38319d9867381998066473ffa1e11c2d360392`
- This file after the removals: 55 918 bytes,
  SHA-256 `3f933ef67c5d0cd2afa28e37209d081f34104b239cb31a5c2308546b5ac36032`

CI and local runs read this same file, so a rule disabled here is disabled
everywhere. To pick up newer rules from Microsoft, re-download, re-apply the
removals below, and update the dates and hashes.

## Tool

Tabular Editor 2 (portable), version **2.29.0**, installed **outside** this
repository at `C:\Tools\TabularEditor2`:

- Source: <https://github.com/TabularEditor/TabularEditor/releases/tag/2.29.0>
- `TabularEditor.Portable.zip`, 7 781 396 bytes
- SHA-256 `c0d3a7abda4572baaf3aeedf9cb342ce7ad4d9840e6438d6b13df02267d308a4`

## Local run

Read-only; it analyses the TMDL on disk and changes nothing. Close Power BI
Desktop first only if you want to be sure you are analysing what is saved.

```powershell
Start-Process -Wait -NoNewWindow -PassThru `
  -FilePath "C:\Tools\TabularEditor2\TabularEditor.exe" `
  -ArgumentList '"CDPR_Health_Hub.SemanticModel\definition\database.tmdl"', '-A', '"bpa\BPARules.json"'
```

Exit code 0 means no severity-3 violations; lower-severity findings still
print to stdout, so read the output, not just the code.

## Deliberate exceptions

Objects that break a rule on purpose carry a
`BestPracticeAnalyzer_IgnoreRules` annotation, so the exception travels with
the object in TMDL instead of living in this file.

| Object | Rule | Why |
|---|---|---|
| `'Time Window'[Time Window]` | DATA_COLUMNS_MUST_HAVE_A_SOURCE_COLUMN | A calculation group column has no source column by definition; the rule's scope catches it wrongly. |
| `'Date'[date]` | HIDE_FOREIGN_KEYS | The date table's key and the field behind two slicers. The rule matches on column *name*, so it flags the dimension side because the fact tables have columns called `date` too. |
| `'Date'[year_month]` | MONTH_(AS_A_STRING)_MUST_BE_SORTED | Values look like `2026-11` and already sort correctly as text, so no separate sort column is needed. |
| `'Date'[month_start]` | MONTHCOLUMN_FORMATSTRING, FIRST_LETTER_OF_OBJECTS_MUST_BE_CAPITALIZED | Formatted `MMM yyyy` to match `month_name`, where the rule demands `MMMM yyyy`. The name is snake_case like every other column in the table; the capitalisation rule only scopes calculated columns, so it flags this one and not its neighbours. |
| `'Event'[event_type_label]`, `[event_type_sort]` | FIRST_LETTER_OF_OBJECTS_MUST_BE_CAPITALIZED | Calculated columns, so the rule reaches them; they are snake_case like every other column in `Event`, including the `event_type` they are derived from. Capitalising two of fourteen would be the inconsistency. |
| `'_Measures'` | REDUCE_USAGE_OF_CALCULATED_TABLES, ENSURE_TABLES_HAVE_RELATIONSHIPS | A measure container is the standard pattern; it holds no data and needs no relationship. |
| `'_Measures'[Value]` | UNNECESSARY_COLUMNS | The single placeholder column of that calculated table. It cannot be deleted. |
| `'Security Region Access'` | ENSURE_TABLES_HAVE_RELATIONSHIPS | The RLS mapping table is read by DAX inside the role, not through a relationship. |
| `'Refresh Info'` | ENSURE_TABLES_HAVE_RELATIONSHIPS | Technical table: refresh timestamp. One row from `DateTime.LocalNow()`, no source and no key, so there is nothing to relate it to. |
| `'Event Window'[day_offset]`, `[series_role]`, `[window_phase]` | HIDE_FACT_TABLE_COLUMNS | Attributes report authors build the event charts from, so they stay visible. |
| `'Event Window'[appid]` | REMOVE_REDUNDANT_COLUMNS_IN_RELATED_TABLES, UNNECESSARY_COLUMNS | The series identifier: the game of that row, either the event's own game or one of the controls. The relationship to `Game` runs through `target_appid`, so both rules read this column as a copy of `Game[appid]`. |
| `[Avg Score Change 2w (pp)]`, `[Avg Net Score Change 2w (pp)]`, `[Recent vs All-time (pp)]` | INTEGER_FORMATTING | Percentage points read better with one decimal; `#,0` would hide the detail. |
| `[Bugs Share CY (to date)]` | INTEGER_FORMATTING | It carries a dynamic format string, which the engine will not allow alongside a static one, so `FormatString` is empty and the rule reads that as unformatted. |
| `[Data Through]`, `[Last Refreshed]`, `[Major Events In Month]`, `[Key Event In Month]`, `[Main Complaint]`, `[Recent Delta Colour]`, `[Bugs Card Colour]` | PROVIDE_FORMAT_STRING_FOR_MEASURES, INTEGER_FORMATTING | They return text, not a number, so a numeric format string has nothing to format. Both rules match on `FormatString` alone, with no data type check, so they flag every text measure. |
| role `Regional access` | REMOVE_ROLES_WITH_NO_MEMBERS | A PBIP project has no members; they are assigned in the Power BI Service. |
| table permissions `Language`, `Security Region Access` | CHECK_IF_DYNAMIC_ROW_LEVEL_SECURITY_(RLS)_IS_NECESSARY | Dynamic RLS is the requirement here, not an accident. |

## Removed rules

Rules that do not fit this project, removed from `BPARules.json` rather than
annotated object by object.

### `DATECOLUMN_FORMATSTRING` — [Formatting] Provide format string for "Date" columns

The rule demands the format string be literally `mm/dd/yyyy`. It rejects
`Long Date` and ISO `yyyy-mm-dd` alike, so on a model with
`sourceQueryCulture: en-GB` it does not check that a date column *has* a
format — it checks that the format is American.

### `RELATIONSHIP_COLUMNS_SHOULD_BE_OF_INTEGER_DATA_TYPE` — [Formatting] Relationship columns should be of integer data type

It wants `Int64` on all 12 relationship columns. Relating on a date column is
the recommended shape for a date table, and `language` / `topic` are the
natural codes the dbt marts produce. Satisfying it would mean adding
surrogate keys throughout — a remodel, not a formatting fix.

### `PARTITION_NAME_SHOULD_MATCH_TABLE_NAME_FOR_SINGLE_PARTITION_TABLES` — [Naming Conventions]

Partition names deliberately carry the dbt mart that feeds the table
(`marts fct_reviews_daily` rather than `Reviews Daily`), which is the more
useful thing to see when a refresh fails.
