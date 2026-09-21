#!/usr/bin/env python3
"""
verify_narrative.py の 8言語テストランナー
- tools/verify-fixtures/*.json を順次実行
- 各フィクスチャ名 (キー '_expect' 等) を解析して PASS/FAIL を判定
- 結果を JSON (verify-results/results.json) と Markdown (docs/verify-test-report.md) に保存
"""
import sys, os, json, subprocess, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCRIPT = ROOT / "verify_narrative.py"
FIX_DIR = ROOT / "verify-fixtures"
RES_DIR = ROOT / "verify-results"
RES_DIR.mkdir(exist_ok=True)
REPORT_MD = ROOT.parent / "docs" / "verify-test-report.md"

PY = sys.executable

# 期待値の期待ルール
# _expect.status: 'pass' | 'pass_with_warning' | 'retry' | 'escalate'
# _expect.retry_in: int (出力 retry がこれと一致するか)
# _expect.must_failed: list[str]
# _expect.should_failed: list[str]
# _expect.char_count_ok: bool | None (None は確認しない)

def run_one(fix_path: Path, payload):
    """1 フィクスチャを実行し、(stdout, exit_code) を返す
    v1.1.2: verify_narrative.py は --locale/--text 形式
    """
    locale = payload.get("locale", "ja")
    text = payload.get("text", "")
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"  # Python 3.7+: 標準入出力・既定 fs encoding を UTF-8 にする
    proc = subprocess.run(
        [PY, str(SCRIPT), "--locale", locale, "--text", text],
        capture_output=True, text=True, encoding="utf-8", env=env
    )
    return proc.stdout, proc.stderr, proc.returncode

def load_expected(fix_path: Path):
    """_expect キーがあれば返す (取り除いた dict も返す)"""
    with open(fix_path, encoding="utf-8") as f:
        d = json.load(f)
    exp = d.pop("_expect", None)
    return d, exp

def evaluate(fix_path: Path):
    name = fix_path.stem
    payload, exp = load_expected(fix_path)
    out, err, code = run_one(fix_path, payload)
    try:
        result = json.loads(out) if out.strip() else {}
    except Exception as e:
        result = {"_parse_error": str(e), "_raw_stdout": out, "_raw_stderr": err}
    record = {
        "name": name,
        "path": str(fix_path),
        "exit_code": code,
        "expected": exp,
        "payload": payload,
        "actual": result,
    }
    # PASS判定
    reasons = []
    if exp is None:
        # 期待値なし → 実行できればOK
        passed = (code in (0,1)) and "_parse_error" not in result
    else:
        passed = True
        if "status" in exp and result.get("status") != exp["status"]:
            passed = False
            reasons.append(f"status: expected={exp['status']} actual={result.get('status')}")
        if "retry_in" in exp and result.get("retry") != exp["retry_in"]:
            passed = False
            reasons.append(f"retry: expected={exp['retry_in']} actual={result.get('retry')}")
        if "must_failed" in exp:
            actual_mf = sorted(result.get("must_failed", []) or [])
            exp_mf = sorted(exp["must_failed"])
            if actual_mf != exp_mf:
                passed = False
                reasons.append(f"must_failed: expected={exp_mf} actual={actual_mf}")
        if "should_failed" in exp:
            actual_sf = sorted(result.get("should_failed", []) or [])
            exp_sf = sorted(exp["should_failed"])
            if actual_sf != exp_sf:
                passed = False
                reasons.append(f"should_failed: expected={exp_sf} actual={actual_sf}")
        if "exit_code" in exp and code != exp["exit_code"]:
            passed = False
            reasons.append(f"exit_code: expected={exp['exit_code']} actual={code}")
    record["passed"] = passed
    record["reasons"] = reasons
    return record

def collect_fixtures():
    files = []
    for p in sorted(FIX_DIR.glob("*.json")):
        files.append(p)
    return files

def write_results_json(results):
    out_path = RES_DIR / "results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    return out_path

def write_report_md(results):
    REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    A = lines.append
    A("# verify_narrative.py テストレポート")
    A("")
    A(f"実行日時: {__import__('datetime').datetime.now().isoformat(timespec='seconds')}")
    A(f"対象スクリプト: `tools/verify_narrative.py`")
    A(f"フィクスチャ: `tools/verify-fixtures/*.json` (合計 {len(results)} 件)")
    A("")
    pass_cnt = sum(1 for r in results if r["passed"])
    fail_cnt = len(results) - pass_cnt
    A(f"## サマリ: {pass_cnt} PASS / {fail_cnt} FAIL (合計 {len(results)})")
    A("")
    A("| # | name | status(actual) | retry(actual) | must_failed | should_failed | PASS/FAIL | 備考 |")
    A("|---|------|----------------|---------------|-------------|---------------|-----------|------|")
    for i, r in enumerate(results, 1):
        a = r["actual"]
        st = a.get("status", "ERR")
        rt = a.get("retry", "-")
        mf = ",".join(a.get("must_failed", []) or []) or "-"
        sf = ",".join(a.get("should_failed", []) or []) or "-"
        pf = "PASS" if r["passed"] else "FAIL"
        note = "; ".join(r["reasons"]) if r["reasons"] else ""
        A(f"| {i} | `{r['name']}` | `{st}` | {rt} | {mf} | {sf} | **{pf}** | {note} |")
    A("")
    A("## 各テストケース詳細")
    for i, r in enumerate(results, 1):
        a = r["actual"]
        A(f"### {i}. `{r['name']}`")
        A("")
        A(f"- locale: `{r['payload'].get('locale')}`")
        A(f"- retry (input): {r['payload'].get('retry',0)}")
        A(f"- expected: `{json.dumps(r['expected'], ensure_ascii=False) if r['expected'] else '(なし)'}`")
        A(f"- actual status: `{a.get('status','ERR')}`")
        if "retry" in a:
            A(f"- actual retry: `{a.get('retry')}`")
        if "must_failed" in a:
            A(f"- must_failed: `{a.get('must_failed')}`")
        if "should_failed" in a:
            A(f"- should_failed: `{a.get('should_failed')}`")
        A(f"- exit_code: {r['exit_code']}")
        A(f"- **判定: {'PASS' if r['passed'] else 'FAIL'}**")
        if r["reasons"]:
            A(f"- 理由: {' / '.join(r['reasons'])}")
        # results details
        if "results" in a:
            A("- 個別ルール結果:")
            for rule in a["results"]:
                ok = "PASS" if rule.get("ok") else "FAIL"
                A(f"  - {ok} {rule.get('rule')} (sev={rule.get('severity')}): {json.dumps(rule, ensure_ascii=False)}")
        A("")
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")
    return REPORT_MD

def main():
    fixtures = collect_fixtures()
    results = []
    for f in fixtures:
        rec = evaluate(f)
        results.append(rec)
        # 簡易ログ
        status = rec["actual"].get("status", "ERR")
        pf = "PASS" if rec["passed"] else "FAIL"
        print(f"[{pf}] {rec['name']}: status={status}")
        if rec["reasons"]:
            for rs in rec["reasons"]:
                print(f"      - {rs}")
    write_results_json(results)
    md_path = write_report_md(results)
    pass_cnt = sum(1 for r in results if r["passed"])
    print(f"\n合計: {pass_cnt}/{len(results)} PASS")
    print(f"results.json: {RES_DIR / 'results.json'}")
    print(f"report md:    {md_path}")
    return 0 if pass_cnt == len(results) else 1

if __name__ == "__main__":
    sys.exit(main())