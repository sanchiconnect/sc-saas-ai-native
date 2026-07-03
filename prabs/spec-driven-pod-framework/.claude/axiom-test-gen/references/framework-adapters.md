# Framework Adapters & Detection — AxiomTestGen Reference

## Detection Order (Step 2)
1. **Project metadata** — strongest signal:
   - `pyproject.toml` / `setup.cfg` / `requirements*.txt` → Python
   - `package.json` (`devDependencies`) → JS/TS
   - `go.mod` → Go · `pom.xml`/`build.gradle` → Java/Kotlin · `Cargo.toml` → Rust
2. **Existing `tests/` idioms** — match the framework already in use; never introduce a second framework.
3. **Dev-dependency names** — `pytest`, `unittest`, `jest`, `vitest`, `mocha`, `junit`, `testng`, `go test`, `cargo test`.
4. If 1–3 disagree or are silent → **ask the user** (do not guess).

## Per-Framework Idioms
| Lang | Default framework | Test file | Fixture/mocking | Property lib | Param/data-driven |
|------|-------------------|-----------|------------------|--------------|-------------------|
| Python | pytest | `test_<mod>.py` | `@pytest.fixture`, `monkeypatch`, `freezegun` | `hypothesis` | `@pytest.mark.parametrize` |
| TS/JS | jest / vitest | `<mod>.test.ts` | `jest.fn()`, `vi.useFakeTimers()` | `fast-check` | `test.each` |
| Java | JUnit 5 | `<Mod>Test.java` | Mockito, `Clock.fixed` | jqwik | `@ParameterizedTest` |
| Go | `testing` | `<mod>_test.go` | interfaces + fakes | `testing/quick` | table-driven tests |
| Rust | built-in | `#[cfg(test)]` | trait fakes | `proptest` | macro tables |

## Determinism Rules (all frameworks)
- Freeze time (`freezegun` / fake timers / injected `Clock`) — never read wall-clock.
- Seed any randomness; prefer property libs with fixed seeds.
- Mock I/O (network, fs, db) at the boundary; integration tests use ephemeral/in-memory fixtures.
- No reliance on test execution order; each test self-contained.

## Output Conventions
- Mirror the repo's existing test directory layout.
- One test module per source module under test.
- Group cases by AC using the framework's class/describe block, with the AC ID in the group name.
