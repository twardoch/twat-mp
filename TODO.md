# TODO for MVP Streamlining

- [x] **Phase 1: Confirm MVP Scope**
  - [x] Confirm async features (`AsyncMultiPool`, `apmap`) are out of scope for MVP v1.0.

- [x] **Phase 2: Refine Project Metadata and Documentation**
  - [x] Update `README.md` for MVP scope (sync focus, async as experimental).
  - [x] Update `API_REFERENCE.md` for MVP scope.
  - [x] Update `docs/architecture.md` for MVP scope.
  - [x] Correct project description in `.cursor/rules/0project.mdc`.
  - [x] Consolidate `LOG.md` into `CHANGELOG.md` and delete `LOG.md`.
  - [x] Review and remove `VERSION.txt` if redundant with `hatch-vcs`.

- [x] **Phase 3: Streamline Codebase for MVP**
  - [x] Ensure `src/twat_mp/__init__.py` exports only MVP synchronous components + `WorkerError`.
  - [x] Isolate `src/twat_mp/async_mp.py` (unused by `__init__.py` for MVP).
  - [x] Review `src/twat_mp/mp.py` (`MultiPool.__enter__` patching, `mmap` factory) for MVP suitability.
  - [x] Update `pyproject.toml`: `aiomultiprocess` as optional `[aio]` extra, ensure async tests skipped by default.

- [x] **Phase 4: Refine `cleanup.py` and Meta-Files**
  - [x] Update `cleanup.py`: Remove `LOG.md` from `REQUIRED_FILES` and docstring.
  - [x] Update `cleanup.py`: Ensure `_run_checks` uses pytest args to ignore async tests.
  - [x] Add `CLEANUP.txt` and `REPO_CONTENT.txt` to `.gitignore`.

- [x] **Phase 5: Testing Review**
  - [x] Adjust `tests/test_async_mp.py` imports to use `twat_mp.async_mp` for independent execution.
  - [x] Ensure default test configurations skip async tests.
  - [x] Review `tests/test_twat_mp.py` and `tests/test_benchmark.py` for MVP scope.

- [x] **Phase 6: Create Planning Documents (This Task)**
  - [x] Write detailed plan to `PLAN.md`.
  - [x] Create summarized checklist in `TODO.md` (and update with progress).

- [x] **Phase 7: Implementation**
  - [x] Execute all planned changes (covered by completing Phases 1-5).
  - [ ] Update `CHANGELOG.md` with all changes.

- [ ] **Phase 8: Final Review and Submission**
  - [ ] Run all checks (`cleanup.py status`).
  - [ ] Perform a final review of all changes and documentation.
  - [ ] Submit with appropriate branch name and commit message.
