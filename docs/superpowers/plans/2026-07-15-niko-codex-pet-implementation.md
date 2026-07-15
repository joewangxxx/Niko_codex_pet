# Niko Codex Pet v2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create, validate, package, and install a smooth modern-pixel-art Niko Codex Pet using the approved character references and the complete Codex Pet v2 contract.

**Architecture:** The parent prepares and owns one deterministic hatch-pet run under `C:\Users\29929\Desktop\codex_pets_Niko\run\niko`. Isolated imagegen workers generate one visual job each from the prepared prompts and grounding inputs; existing hatch-pet scripts extract, validate, assemble, despill, and render QA artifacts. Only a final `1536x2288` validated v2 atlas and manifest are installed.

**Tech Stack:** Installed `hatch-pet` scripts, built-in `imagegen`, bundled Python `C:\Users\29929\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`, Pillow, PowerShell, PNG/WebP/JSON.

## Global Constraints

- Pet id: `niko`; display name: `Niko`; style preset: `pixel`.
- Final atlas: `1536x2288`, 8 columns × 11 rows, `192x208` cells.
- Package manifest: `spriteVersionNumber: 2` and `spritesheetPath: "spritesheet.webp"`.
- Brown swept hair, neat full brown beard, blue eyes, green-and-white geometric jersey, black pants, white shoes.
- No readable text, detailed logos, pants swirl, shadows, detached effects, or scenery.
- The medal appears only in the `waving` row and remains physically attached as a worn prop.
- Generate visual jobs only with `imagegen`; never synthesize missing visual rows with local drawing code.
- Every standard row is independently generated except a visually approved deterministic `running-left` mirror.
- Look rows are coherent eight-pose generations; never package an individually repaired look cell.
- Final chroma cleanup runs exactly once on the complete 8×11 atlas.
- The workspace is not a Git repository, so the plan does not create commits or initialize repository metadata.

---

### Task 1: Prepare the Niko run

**Files:**
- Create: `C:\Users\29929\Desktop\codex_pets_Niko\run\niko\pet_request.json`
- Create: `C:\Users\29929\Desktop\codex_pets_Niko\run\niko\imagegen-jobs.json`
- Create: `C:\Users\29929\Desktop\codex_pets_Niko\run\niko\prompts\`
- Create: `C:\Users\29929\Desktop\codex_pets_Niko\run\niko\references\layout-guides\`

**Interfaces:**
- Consumes: approved design spec and three reference PNG files.
- Produces: the authoritative request, chroma key, generated prompts, layout guides, and dependency-aware visual job manifest.

- [ ] **Step 1: Run the preparation script**

```powershell
& 'C:\Users\29929\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  'C:\Users\29929\.codex\skills\hatch-pet\scripts\prepare_pet_run.py' `
  --pet-name 'Niko' `
  --pet-id 'niko' `
  --display-name 'Niko' `
  --description 'A modern pixel-art chibi pet inspired by the esports player Niko.' `
  --reference 'C:\Users\29929\Downloads\ChatGPT Image 2026年7月15日 17_35_22.png' `
  --reference 'C:\Users\29929\Downloads\ChatGPT Image 2026年7月15日 17_35_16.png' `
  --reference 'C:\Users\29929\Desktop\codex_pets_Niko\concepts\niko-style-pixel.png' `
  --output-dir 'C:\Users\29929\Desktop\codex_pets_Niko\run\niko' `
  --pet-notes 'Modern hard-edged pixel-art chibi adult male with swept medium-brown hair, neat full brown beard, blue eyes, simplified green-and-white geometric jersey, plain black athletic pants without symbols, and white sneakers. Compact readable silhouette. No text or detailed logos. No medal except as a worn attached prop in the waving celebration row.' `
  --style-preset pixel `
  --style-notes 'Intentional chunky pixel clusters, crisp hard edges, limited rich palette, no antialiasing appearance, no smooth vector or painterly rendering.' `
  --chroma-key auto `
  --force
```

Expected: exit code `0`; `pet_request.json` and `imagegen-jobs.json` exist.

- [ ] **Step 2: Verify the generated contract**

```powershell
$run = 'C:\Users\29929\Desktop\codex_pets_Niko\run\niko'
$request = Get-Content -Raw -LiteralPath "$run\pet_request.json" | ConvertFrom-Json
$jobs = Get-Content -Raw -LiteralPath "$run\imagegen-jobs.json" | ConvertFrom-Json
[pscustomobject]@{
  pet_id = $request.pet_id
  style = $request.style.preset
  chroma = $request.chroma_key.hex
  jobs = $jobs.jobs.Count
  base_ready = (($jobs.jobs | Where-Object id -eq 'base').depends_on.Count -eq 0)
}
```

Expected: `pet_id=niko`, `style=pixel`, `jobs=13`, and `base_ready=True`.

### Task 2: Establish the canonical Niko identity

**Files:**
- Create: `C:\Users\29929\Desktop\codex_pets_Niko\run\niko\decoded\base.png`
- Create: `C:\Users\29929\Desktop\codex_pets_Niko\run\niko\references\canonical-base.png`
- Modify: `C:\Users\29929\Desktop\codex_pets_Niko\run\niko\imagegen-jobs.json`

**Interfaces:**
- Consumes: `prompts\base-pet.md` and every base job input image from the manifest.
- Produces: `workerSelectedSource`, the absolute Windows path returned in the worker's `selected_source` field, plus one approved full-body pixel-art identity anchor used by all row workers.

- [ ] **Step 1: Dispatch one isolated base worker**

The worker reads `prompts\base-pet.md`, attaches all listed references, invokes only the built-in imagegen path, verifies one centered full-body sprite on a flat chroma background, and returns exactly two fields: `selected_source` containing an absolute Windows path string and `qa_note` containing one sentence.

- [ ] **Step 2: Copy the selected file into the run**

```powershell
$source = $workerSelectedSource
$run = 'C:\Users\29929\Desktop\codex_pets_Niko\run\niko'
New-Item -ItemType Directory -Force -Path "$run\decoded", "$run\references" | Out-Null
Copy-Item -LiteralPath $source -Destination "$run\decoded\base.png" -Force
Copy-Item -LiteralPath "$run\decoded\base.png" -Destination "$run\references\canonical-base.png" -Force
```

Expected: both files exist, have identical byte lengths, and the worker reports no identity, layout, text, shadow, or detached-effect failure.

- [ ] **Step 3: Mark `base` complete only after the copies exist**

Update the `base` object in `imagegen-jobs.json` to contain `status: "complete"`, the exact selected `source_path`, and an ISO-8601 UTC `completed_at`. Remove the selected original if it resides under `C:\Users\29929\.codex\generated_images` after verifying the decoded copy.

### Task 3: Generate and validate the nine standard animation rows

**Files:**
- Create: `C:\Users\29929\Desktop\codex_pets_Niko\run\niko\decoded\{idle,running-right,running-left,waving,jumping,failed,waiting,running,review}.png`
- Create: `C:\Users\29929\Desktop\codex_pets_Niko\run\niko\qa\rows\$row\review.json` for each exact manifest row id.
- Modify: `C:\Users\29929\Desktop\codex_pets_Niko\run\niko\imagegen-jobs.json`

**Interfaces:**
- Consumes: each job prompt, retry prompt, canonical base, original identity references, and matching layout guide exactly as listed in the manifest.
- Produces: nine complete row strips that pass component extraction and per-row structural inspection.

- [ ] **Step 1: Generate `idle` and `running-right` with two isolated workers**

Each worker handles one job, attaches every manifest input, uses imagegen only, validates exact pose count, spacing, identity, flat chroma background, complete bodies, and forbidden effects, and returns only `selected_source` and `qa_note`.

- [ ] **Step 2: Copy and deterministically inspect each generated row**

For each row id, copy the selected source to its manifest `output_path`, then run:

```powershell
$python = 'C:\Users\29929\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
$skill = 'C:\Users\29929\.codex\skills\hatch-pet'
$run = 'C:\Users\29929\Desktop\codex_pets_Niko\run\niko'
$row = 'idle'
& $python "$skill\scripts\extract_strip_frames.py" --decoded-dir "$run\decoded" --output-dir "$run\qa\rows\$row\frames" --states $row --method auto
& $python "$skill\scripts\inspect_frames.py" --frames-root "$run\qa\rows\$row\frames" --json-out "$run\qa\rows\$row\review.json" --states $row --require-components
```

Expected: both commands exit `0`; the row review contains no errors. Only then mark the row job complete and remove the original generated file.

- [ ] **Step 3: Decide the left-running strategy**

Approve deterministic mirroring only if `running-right` contains no asymmetric logo, medal, lighting, or handed prop. The approved Niko design is intentionally mirror-safe; if worker QA confirms this, run:

```powershell
& 'C:\Users\29929\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  'C:\Users\29929\.codex\skills\hatch-pet\scripts\derive_running_left_from_running_right.py' `
  --run-dir 'C:\Users\29929\Desktop\codex_pets_Niko\run\niko' `
  --confirm-appropriate-mirror `
  --decision-note 'The approved jersey and pants use no side-specific text, logo, medal, lighting, or handed prop, so per-slot mirroring preserves identity and timing.'
```

Expected: `decoded\running-left.png` is created and the manifest records a complete derived job. If the right row contains an asymmetric feature, generate `running-left` through its normal imagegen worker instead.

- [ ] **Step 4: Generate the remaining rows with up to three isolated workers active**

Generate `waving`, `jumping`, `failed`, `waiting`, `running`, and `review` as separate visual jobs. Enforce the frame counts `4`, `5`, `8`, `6`, `6`, and `6`. Only `waving` may contain the worn medal. Apply Step 2 immediately to every completed row before marking it complete.

- [ ] **Step 5: Assemble and inspect the standard atlas**

```powershell
$python = 'C:\Users\29929\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
$skill = 'C:\Users\29929\.codex\skills\hatch-pet'
$run = 'C:\Users\29929\Desktop\codex_pets_Niko\run\niko'
& $python "$skill\scripts\extract_strip_frames.py" --decoded-dir "$run\decoded" --output-dir "$run\frames" --states all --method auto
& $python "$skill\scripts\inspect_frames.py" --frames-root "$run\frames" --json-out "$run\qa\review.json" --require-components
& $python "$skill\scripts\compose_atlas.py" --frames-root "$run\frames" --output "$run\final\spritesheet.png" --webp-output "$run\final\spritesheet.webp"
& $python "$skill\scripts\make_contact_sheet.py" "$run\final\spritesheet.webp" --output "$run\qa\contact-sheet.png"
& $python "$skill\scripts\render_animation_previews.py" --frames-root "$run\frames" --output-dir "$run\qa\previews"
```

Expected: all commands exit `0`; `qa\review.json` has no errors; the contact sheet and GIFs show consistent identity, correct row semantics, alternating directional gait, visible idle micro-motion, and no extraction-induced scale or baseline popping.

### Task 4: Build and approve the 16-direction look family

**Files:**
- Create: `C:\Users\29929\Desktop\codex_pets_Niko\run\niko\qa\look-mechanics.md`
- Create: `C:\Users\29929\Desktop\codex_pets_Niko\run\niko\decoded\look-cardinals.png`
- Create: `C:\Users\29929\Desktop\codex_pets_Niko\run\niko\decoded\look-anchors-approved.png`
- Create: `C:\Users\29929\Desktop\codex_pets_Niko\run\niko\decoded\look-row-9.png`
- Create: `C:\Users\29929\Desktop\codex_pets_Niko\run\niko\decoded\look-row-10.png`

**Interfaces:**
- Consumes: canonical base, approved standard contact sheet, cardinal layout guide, and look-row guides.
- Produces: four approved cardinal pose families and two coherent eight-pose clockwise rows.

- [ ] **Step 1: Write the Niko-specific look mechanics decision**

Record that eyes, eyelids, and brows lead; head and neck follow with restrained yaw/pitch; hair silhouette and shoulders follow subtly; pelvis, feet, scale, and baseline stay anchored. Define `000` up, `090` screen-right, `180` down, and `270` screen-left with visible pupil and nose landmarks. Set an even motion budget between every adjacent `22.5`-degree pose.

- [ ] **Step 2: Generate and extract the four-cardinal strip**

Dispatch one isolated cardinal worker using `prompts\look-cardinals.md`, all listed inputs, and `qa\look-mechanics.md`. Copy the selected source, then run:

```powershell
$request = Get-Content -Raw -LiteralPath 'C:\Users\29929\Desktop\codex_pets_Niko\run\niko\pet_request.json' | ConvertFrom-Json
$key = $request.chroma_key.hex
$python = 'C:\Users\29929\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
$skill = 'C:\Users\29929\.codex\skills\hatch-pet'
$run = 'C:\Users\29929\Desktop\codex_pets_Niko\run\niko'
& $python "$skill\scripts\extract_cardinal_anchors.py" --strip "$run\decoded\look-cardinals.png" --output-dir "$run\decoded\look-anchors" --chroma-key $key --json-out "$run\qa\cardinal-anchors.json"
& $python "$skill\scripts\compose_cardinal_anchor_strip.py" --anchors-dir "$run\decoded\look-anchors" --output "$run\decoded\look-anchors-approved.png"
```

Expected: all four cells pass clipping checks and the worker reports concrete landmarks proving up, right, down, and left.

- [ ] **Step 3: Generate and register row 9**

Dispatch one isolated row worker for `look-row-9` using every manifest input. Copy the coherent eight-pose result, then run:

```powershell
& 'C:\Users\29929\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  'C:\Users\29929\.codex\skills\hatch-pet\scripts\assemble_extended_atlas.py' `
  --base-atlas 'C:\Users\29929\Desktop\codex_pets_Niko\run\niko\final\spritesheet.webp' `
  --look-row-9 'C:\Users\29929\Desktop\codex_pets_Niko\run\niko\decoded\look-row-9.png' `
  --neutral-cell 'C:\Users\29929\Desktop\codex_pets_Niko\run\niko\frames\idle\00.png' `
  --chroma-key $key --chroma-threshold 96 `
  --registered-row-output 'C:\Users\29929\Desktop\codex_pets_Niko\run\niko\qa\look-row-9-registered.png' `
  --registration-manifest-output 'C:\Users\29929\Desktop\codex_pets_Niko\run\niko\qa\look-row-9-registration.json'
```

Expected: ordered pose recovery and post-registration edge checks pass. Mark row 9 complete only after labeled semantics confirm `000` through `157.5` without wrong quadrants, reversal, scale pop, or registration jump.

- [ ] **Step 4: Generate row 10 only after row 9 passes**

Dispatch one isolated worker with the approved cardinal strip and completed row 9 as continuity evidence. Copy the complete coherent row 10 result. Do not patch individual cells.

### Task 5: Assemble, blind-test, visually review, package, and install v2

**Files:**
- Create: `C:\Users\29929\Desktop\codex_pets_Niko\run\niko\final\spritesheet-extended.webp`
- Create: `C:\Users\29929\Desktop\codex_pets_Niko\run\niko\final\validation-extended.json`
- Create: `C:\Users\29929\Desktop\codex_pets_Niko\run\niko\qa\contact-sheet-extended.png`
- Create: `C:\Users\29929\Desktop\codex_pets_Niko\run\niko\qa\look-directions.png`
- Create: `C:\Users\29929\Desktop\codex_pets_Niko\run\niko\qa\direction-semantics.json`
- Create: `C:\Users\29929\Desktop\codex_pets_Niko\run\niko\qa\direction-blind-validation.json`
- Create: `C:\Users\29929\Desktop\codex_pets_Niko\run\niko\qa\look-continuity.json`
- Create: `C:\Users\29929\.codex\pets\niko\pet.json`
- Create: `C:\Users\29929\.codex\pets\niko\spritesheet.webp`

**Interfaces:**
- Consumes: validated standard atlas, registered row 9, coherent row 10, neutral idle cell, chroma key, and all QA reports.
- Produces: one installed Codex Pet v2 package and retained evidence that every hard gate passed.

- [ ] **Step 1: Assemble, despill once, and validate**

Run `assemble_extended_atlas.py` with the persisted row-9 registration and row 10, then run `despill_chroma_edges.py` exactly once and `validate_atlas.py --require-v2`. Expected: atlas dimensions `1536x2288`, despill `ok: true`, validation `ok: true`, used cells non-empty, and unused cells transparent.

- [ ] **Step 2: Generate focused QA media and continuity evidence**

Run `make_contact_sheet.py`, `make_direction_qa_sheet.py`, `make_direction_blind_qa_sheet.py`, and `measure_direction_continuity.py` against the extended atlas. Expected: all outputs exist and no deterministic command fails.

- [ ] **Step 3: Run three isolated blind direction reviewers**

Each fresh worker receives only `qa\direction-blind-pairs.png` with `fork_turns="none"`. Save each exact JSON verdict separately, combine them with `combine_direction_blind_verdicts.py`, and validate consensus with `validate_direction_blind_verdicts.py`. Expected: both cardinal pairs pass; intermediate warnings may remain for labeled review.

- [ ] **Step 4: Run one independent final visual QA worker**

The worker inspects the standard and extended contact sheets, all preview GIFs, focused direction sheet, blind validation, continuity report, standard review, and v2 validation. Persist explicit `pass`, `warning`, or `fail` semantics for all 16 directions with horizontal and vertical evidence. Any major failure regenerates only the smallest complete standard row or coherent look row and repeats all affected checks.

- [ ] **Step 5: Install only after every hard gate passes**

Copy `final\spritesheet-extended.webp` to `C:\Users\29929\.codex\pets\niko\spritesheet.webp` and create:

```json
{
  "id": "niko",
  "displayName": "Niko",
  "description": "A modern pixel-art chibi pet inspired by the esports player Niko.",
  "spriteVersionNumber": 2,
  "spritesheetPath": "spritesheet.webp"
}
```

Write `qa\run-summary.json` with the run directory, spritesheet, validation, despill, contact sheet, direction sheet, direction semantics, blind validation, optional minor-resolution file, continuity report, standard review, and package directory.

- [ ] **Step 6: Final verification**

Re-run `validate_atlas.py --require-v2` on the installed spritesheet and parse `pet.json`. Expected: validation succeeds; the installed asset is `1536x2288`; `spriteVersionNumber` equals `2`; both package files exist together.
