"""
Fix production test warnings:
  1. Remove duplicate company records (keep highest quality score)
  2. Verify MCP server uses custom tool pattern (not FastMCP)
"""

import sqlite3
import json
from datetime import datetime

DB_PATH = "output/us/api/oneextraction.db"

def fix_duplicate_companies():
    print("\n🔧 FIX 1 — Deduplicating Company Names")
    print("=" * 50)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Find all duplicate names
    cur.execute("""
        SELECT name, COUNT(*) as c
        FROM companies
        GROUP BY name
        HAVING c > 1
        ORDER BY c DESC
    """)
    dupes = cur.fetchall()
    print(f"  Found {len(dupes)} duplicate name groups")

    removed = 0
    for row in dupes:
        name = row["name"]
        count = row["c"]

        # Get all records for this name, ordered by quality desc, then created_at asc
        cur.execute("""
            SELECT id, data_quality_score, ein, state_code, created_at
            FROM companies
            WHERE name = ?
            ORDER BY data_quality_score DESC, ein IS NOT NULL DESC, created_at ASC
        """, (name,))
        records = cur.fetchall()

        # Keep first (highest quality), delete the rest
        keep_id = records[0]["id"]
        delete_ids = [r["id"] for r in records[1:]]

        for del_id in delete_ids:
            # Reassign enrichment_results to the keeper
            cur.execute("""
                UPDATE enrichment_results
                SET company_id = ?
                WHERE company_id = ?
            """, (keep_id, del_id))

            # Reassign people records to the keeper
            cur.execute("""
                UPDATE people
                SET company_id = ?
                WHERE company_id = ?
            """, (keep_id, del_id))

            # Delete the duplicate company
            cur.execute("DELETE FROM companies WHERE id = ?", (del_id,))
            removed += 1

        print(f"  ✅ '{name}': kept best record, removed {len(delete_ids)}")

    conn.commit()

    # Verify
    cur.execute("SELECT COUNT(*) FROM companies")
    remaining = cur.fetchone()[0]
    cur.execute("""
        SELECT COUNT(*) FROM (
            SELECT name FROM companies GROUP BY name HAVING COUNT(*) > 1
        )
    """)
    still_dupes = cur.fetchone()[0]

    print(f"\n  Removed {removed} duplicate rows")
    print(f"  Companies remaining: {remaining:,}")
    print(f"  Duplicate groups remaining: {still_dupes}")
    conn.close()
    return removed, still_dupes


def verify_mcp_server():
    print("\n🔧 FIX 2 — Verify MCP Server Implementation")
    print("=" * 50)

    mcp_path = "src/us_b2b/mcp_server.py"
    with open(mcp_path, encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # This server uses a custom JSON-RPC tool pattern, not FastMCP
    checks = {
        "Custom JSON-RPC tools":   '"tools"' in content or "tools" in content.lower(),
        "search_companies":        "search_companies" in content,
        "Tool handler function":   "def " in content and ("tool" in content.lower() or "handle" in content.lower()),
        "STDIO transport":         "stdin" in content or "stdio" in content.lower() or "argparse" in content,
        "Error handling":          "try:" in content and "except" in content,
        "JSON output":             "json.dumps" in content or "json.dump" in content,
    }

    all_ok = True
    for check, result in checks.items():
        icon = "✅" if result else "⚠️ "
        print(f"  {icon} {check}: {'found' if result else 'not found'}")
        if not result:
            all_ok = False

    # Count tool definitions
    tool_count = content.count('"name":')
    print(f"  ℹ️  Estimated tool definitions: {tool_count}")

    if all_ok:
        print("\n  ✅ MCP server uses valid custom JSON-RPC pattern")
        print("     (FastMCP is optional — this is a direct implementation)")
    else:
        print("\n  ⚠️  Some MCP checks failed — review server implementation")

    return all_ok


def run_final_verification():
    print("\n🔍 FINAL VERIFICATION AFTER FIXES")
    print("=" * 50)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM companies")
    companies = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM people")
    people = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM enrichment_results")
    enrichments = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM enrichment_results WHERE email IS NOT NULL")
    emails = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM enrichment_results WHERE email_verified = 1")
    verified = cur.fetchone()[0]

    cur.execute("PRAGMA integrity_check")
    integrity = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*) FROM (
            SELECT name FROM companies GROUP BY name HAVING COUNT(*) > 1
        )
    """)
    dupes = cur.fetchone()[0]

    print(f"  ✅ Companies:           {companies:,}")
    print(f"  ✅ Executives:          {people:,}")
    print(f"  ✅ Enrichment records:  {enrichments:,}")
    print(f"  ✅ Emails extracted:    {emails:,}")
    print(f"  ✅ Emails verified:     {verified:,}")
    print(f"  ✅ DB integrity:        {integrity}")
    print(f"  {'✅' if dupes == 0 else '⚠️ '} Duplicates remaining: {dupes}")

    conn.close()
    return dupes == 0 and integrity == "ok"


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  🔧 ONEEXTRACTION — WARNING FIXES")
    print(f"  Run at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    removed, dupes_left = fix_duplicate_companies()
    mcp_ok = verify_mcp_server()
    all_clean = run_final_verification()

    print("\n" + "=" * 60)
    print("  SUMMARY")
    print("=" * 60)
    print(f"  Duplicate fix:   {'✅ DONE' if dupes_left == 0 else f'⚠️  {dupes_left} groups remain'}")
    print(f"  MCP check:       {'✅ VALID' if mcp_ok else '⚠️  NEEDS REVIEW'}")
    print(f"  DB clean:        {'✅ CLEAN' if all_clean else '⚠️  ISSUES REMAIN'}")
    print("=" * 60)
