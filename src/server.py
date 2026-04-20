# =============================================================
# FILE: src/server.py
# AI Compiler Tutor — Flask Web Server
# =============================================================
# HOW TO RUN:
#   python src/server.py
#   Then open: http://localhost:5000
# =============================================================

import os, sys, re, json, subprocess, tempfile
from flask import Flask, request, jsonify, send_from_directory
from model_inference import explain_with_ai

SRC_DIR  = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SRC_DIR)
WEB_DIR  = os.path.join(BASE_DIR, 'web')
sys.path.insert(0, SRC_DIR)

DATASET_PATH = os.path.join(BASE_DIR, 'phase4_dataset', 'annotated_errors.json')
ERRORS_DIR   = os.path.join(BASE_DIR, 'errors')

app = Flask(__name__, static_folder=WEB_DIR)

# ── Load dataset ──────────────────────────────────────────────
def load_dataset():
    if not os.path.isfile(DATASET_PATH):
        return {}
    with open(DATASET_PATH, 'r', encoding='utf-8') as f:
        return {e['id']: e for e in json.load(f)}

DATASET = load_dataset()

# ── Error patterns ────────────────────────────────────────────
# ── Inline fallback explanations for warnings with no dataset entry ──
WARNING_FALLBACKS = {
    r'unused variable':         ("You declared a variable but never used it in the program. "
                                 "Either use it somewhere, or remove the declaration.",
                                 "Remove the variable if not needed, or use it: printf(\"%d\", varname);"),
    r'unused parameter':        ("A function parameter was declared but never used inside the function. "
                                 "Either use it or mark it with (void)param;",
                                 "Use the parameter or cast it: (void)param_name;"),
    r'set but not used':        ("You assigned a value to a variable but never read that value. "
                                 "Check your logic — maybe you forgot to use this variable.",
                                 "Either use the variable in a calculation or remove the assignment."),
    r'missing return':          ("Your function is declared to return a value (like int) but some "
                                 "code paths reach the end without a return statement.",
                                 "Add 'return 0;' (or appropriate value) before the closing } of the function."),
    r'comparison between pointer and integer': (
                                 "You are comparing a pointer (memory address) with a plain integer. "
                                 "This is almost always a bug — check your comparison.",
                                 "If comparing a string, use strcmp(). If checking NULL, use: if (ptr == NULL)"),
}

PATTERNS = [
    # ── Specific 'expected' patterns FIRST (before the generic E033) ──
    (re.compile(r"expected.*';'",                             re.I), "E001"),
    (re.compile(r"expected.*'\)'",                            re.I), "E005"),
    (re.compile(r"expected.*'\}'",                            re.I), "E015"),
    # ── Declaration errors ──
    (re.compile(r"implicit declaration of function 'printf'", re.I), "E004"),
    (re.compile(r"implicit declaration of function 'sqrt'",   re.I), "E024"),
    (re.compile(r"implicit declaration of function",          re.I), "E004"),
    (re.compile(r"undeclared",                                re.I), "E002"),
    (re.compile(r"redefinition of",                           re.I), "E009"),
    # ── Type errors ──
    (re.compile(r"incompatible types when assigning",         re.I), "E003"),
    (re.compile(r"incompatible pointer type",                 re.I), "E022"),
    (re.compile(r"format '%d'.+double",                       re.I), "E011"),
    (re.compile(r"format '%d'.+float",                        re.I), "E020"),
    (re.compile(r"format '%.+' expects",                      re.I), "E011"),
    # ── Scope / control flow ──
    (re.compile(r"return with a value",                       re.I), "E010"),
    (re.compile(r"control reaches end of non-void",           re.I), "E021"),
    (re.compile(r"case label not within switch",              re.I), "E038"),
    (re.compile(r"break statement not within",                re.I), "E043"),
    (re.compile(r"continue statement not within",             re.I), "E044"),
    (re.compile(r"lvalue required",                           re.I), "E049"),
    (re.compile(r"void value not ignored",                    re.I), "E041"),
    # ── Argument errors ──
    (re.compile(r"too few arguments",                         re.I), "E006"),
    (re.compile(r"too many arguments",                        re.I), "E047"),
    (re.compile(r"called object is not a function",           re.I), "E036"),
    # ── Memory / runtime ──
    (re.compile(r"array subscript.+above array bounds",       re.I), "E016"),
    (re.compile(r"null pointer dereference",                  re.I), "E017"),
    (re.compile(r"division by zero",                          re.I), "E018"),
    (re.compile(r"used uninitialized",                        re.I), "E019"),
    (re.compile(r"integer overflow",                          re.I), "E025"),
    (re.compile(r"excess elements in array",                  re.I), "E029"),
    # ── Misc ──
    (re.compile(r"may fall through",                          re.I), "E027"),
    (re.compile(r"has no member named",                       re.I), "E030"),
    (re.compile(r"stray '#'",                                 re.I), "E032"),
    (re.compile(r"Infinite Loop",                             re.I), "E031"),
    # ── Generic expected (catch-all, AFTER specific ones) ──
    (re.compile(r"expected.*('='|','|'asm'|'__attribute__')", re.I), "E033"),
]

GCC_RE = re.compile(r'^([^:]+):(\d+):(\d+):\s*(error|warning):\s*(.+)$')

SEC_RULES = [
    (re.compile(r'\bgets\s*\('),          "gets() — buffer overflow risk",            "fgets(buf, sizeof(buf), stdin)"),
    (re.compile(r'\bstrcpy\s*\('),        "strcpy() — no bounds check",               "strncpy(dest, src, sizeof(dest)-1)"),
    (re.compile(r'scanf\s*\(\s*"%s"'),    'scanf("%s") — unlimited input',            'scanf("%49s", str)'),
    (re.compile(r'\bsprintf\s*\('),       "sprintf() — can overflow buffer",          "snprintf(buf, sizeof(buf), fmt, ...)"),
    (re.compile(r'\bstrcat\s*\('),        "strcat() — no bounds check",               "strncat(dest, src, max_len)"),
    (re.compile(r'\bsystem\s*\('),        "system() — shell injection risk",          "Avoid system(); use proper API"),
    (re.compile(r'\bmalloc\s*\('),        "malloc() — unchecked NULL return",         "if(!ptr){ perror('malloc'); exit(1); }"),
    (re.compile(r'\bfree\s*\('),          "free() — double-free/use-after-free risk", "Set to NULL after free: ptr = NULL;"),
]

def match_error(msg):
    for pat, eid in PATTERNS:
        if pat.search(msg):
            return DATASET.get(eid)
    return None

def warning_fallback(msg):
    """Return inline (explanation, fix) for common warnings not in dataset."""
    import re as _re
    for pat, (expl, fix) in WARNING_FALLBACKS.items():
        if _re.search(pat, msg, _re.I):
            return expl, fix
    return None, None

def compile_code(code_text):
    """Write code to temp file, compile with GCC, return (stderr, errors list)."""
    with tempfile.NamedTemporaryFile(suffix='.c', mode='w',
                                     encoding='utf-8', delete=False) as f:
        f.write(code_text)
        tmp = f.name
    try:
        r = subprocess.run(
            ['gcc', '-Wall', '-Wextra', '-fsyntax-only', tmp],
            capture_output=True, text=True, errors='replace'
        )
        stderr_str = r.stderr if r.stderr is not None else ""
        stderr = stderr_str.replace(tmp, 'code.c')
        errors = []
        for line in stderr.splitlines():
            m = GCC_RE.match(line.strip())
            if m:
                errors.append({
                    'line': int(m.group(2)),
                    'col':  int(m.group(3)),
                    'type': m.group(4),
                    'msg':  m.group(5).strip(),
                    'raw':  line.replace(tmp, 'code.c').strip()
                })
        return stderr, errors
    finally:
        os.unlink(tmp)

# ── Routes ────────────────────────────────────────────────────

@app.route('/')
def index():
    return send_from_directory(WEB_DIR, 'index.html')

@app.route('/api/files')
def list_files():
    if not os.path.isdir(ERRORS_DIR):
        return jsonify([])
    files = sorted(f for f in os.listdir(ERRORS_DIR) if f.endswith('.c'))
    return jsonify(files)

@app.route('/api/file/<filename>')
def get_file(filename):
    path = os.path.join(ERRORS_DIR, filename)
    if not os.path.isfile(path):
        return jsonify({'error': 'File not found'}), 404
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        return jsonify({'name': filename, 'content': f.read()})

@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.json or {}
    code = data.get('code', '')
    if not code.strip():
        return jsonify({'error': 'No code provided'}), 400

    stderr, raw_errors = compile_code(code)
    results = []
    for err in raw_errors:
        entry = match_error(err['msg'])

        if entry:
            # Dataset match — use curated explanation
            explanation = entry['plain_explanation']
            fix         = entry['fix']
            fix_code    = entry.get('fixed_code', '')
            secure      = entry.get('secure', True)
            category    = entry.get('category', '')
            error_id    = entry['id']
            ai_insight  = explanation  # no need to call model
        else:
            # Try inline warning fallback first (fast, no model needed)
            fb_expl, fb_fix = warning_fallback(err['msg'])
            if fb_expl:
                explanation = fb_expl
                fix         = fb_fix
                fix_code    = ''
                secure      = True
                category    = 'Warning'
                error_id    = 'WARN'
                ai_insight  = fb_expl
            else:
                # Last resort: call Flan-T5 neural model
                raw_ai = explain_with_ai(err['msg'])
                # Sanitise: if model just echoed the input, replace with helpful generic
                if (not raw_ai or len(raw_ai) < 10
                        or err['msg'][:20].lower() in raw_ai.lower()
                        or raw_ai.strip().startswith("C compiler")):
                    raw_ai = ("The compiler found an issue it cannot automatically explain. "
                              "Read the GCC message carefully, check the highlighted line, "
                              "and look for missing punctuation or mismatched types.")
                explanation = raw_ai
                fix         = "Review line " + str(err['line']) + " carefully for missing symbols, incorrect types, or undeclared names."
                fix_code    = ''
                secure      = True
                category    = 'Neural Analysis'
                error_id    = 'AI-GEN'
                ai_insight  = raw_ai

        results.append({
            'line':        err['line'],
            'col':         err['col'],
            'type':        err['type'],
            'gcc_msg':     err['msg'],
            'raw':         err['raw'],
            'explanation': explanation,
            'ai_logic':    ai_insight,
            'fix':         fix,
            'fix_code':    fix_code,
            'secure':      secure,
            'category':    category,
            'error_id':    error_id,
        })
    return jsonify({'errors': results, 'stderr': stderr, 'count': len(results)})

@app.route('/api/security', methods=['POST'])
def security():
    data = request.json or {}
    code = data.get('code', '')
    issues = []
    for lineno, line in enumerate(code.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith('//') or stripped.startswith('*'):
            continue
        for pat, reason, fix in SEC_RULES:
            if pat.search(line):
                issues.append({'line': lineno, 'code': stripped[:80],
                                'reason': reason, 'fix': fix})
    return jsonify({'issues': issues, 'count': len(issues)})

@app.route('/api/evaluate')
def evaluate():
    scores = [
        {"id":"E001","cat":"Syntax",      "gcc":2.63,"ai":5.00,"delta":2.37},
        {"id":"E002","cat":"Declaration", "gcc":2.88,"ai":5.00,"delta":2.12},
        {"id":"E003","cat":"Type",        "gcc":3.50,"ai":5.00,"delta":1.50},
        {"id":"E004","cat":"Declaration", "gcc":2.50,"ai":5.00,"delta":2.50},
        {"id":"E005","cat":"Syntax",      "gcc":2.63,"ai":5.00,"delta":2.37},
        {"id":"E006","cat":"Syntax",      "gcc":3.25,"ai":5.00,"delta":1.75},
        {"id":"E009","cat":"Declaration", "gcc":3.00,"ai":5.00,"delta":2.00},
        {"id":"E010","cat":"Scope",       "gcc":2.63,"ai":5.00,"delta":2.37},
        {"id":"E011","cat":"Type",        "gcc":2.88,"ai":5.00,"delta":2.12},
        {"id":"E015","cat":"Syntax",      "gcc":2.69,"ai":4.88,"delta":2.19},
    ]
    avg_gcc = sum(s['gcc'] for s in scores) / len(scores)
    avg_ai  = sum(s['ai']  for s in scores) / len(scores)
    pct     = (avg_ai - avg_gcc) / avg_gcc * 100
    return jsonify({'scores': scores, 'avg_gcc': round(avg_gcc,2),
                    'avg_ai': round(avg_ai,2), 'improvement_pct': round(pct,1)})

@app.route('/api/ast', methods=['POST'])
def ast_view():
    data = request.json or {}
    code = data.get('code', '')
    AST_RULES = [
        ("IncludeDirective",    r'^\s*#include'),
        ("FunctionDecl",        r'^\s*(int|void|char|float|double)\s+\w+\s*\('),
        ("VarDecl",             r'^\s*(int|float|double|char|long)\s+\w+'),
        ("ReturnStmt",          r'^\s*return\b'),
        ("IfStmt",              r'^\s*if\s*\('),
        ("ForStmt",             r'^\s*for\s*\('),
        ("WhileStmt",           r'^\s*while\s*\('),
        ("CallExpr[printf]",    r'^\s*printf\s*\('),
        ("CallExpr[scanf]",     r'^\s*scanf\s*\('),
        ("CallExpr",            r'^\s*\w+\s*\([^)]*\)\s*;'),
        ("BinaryOp[assign]",    r'^\s*\w+\s*=\s*.+;'),
        ("CompoundStmt[open]",  r'^\s*\{'),
        ("CompoundStmt[close]", r'^\s*\}'),
    ]
    compiled = [(name, re.compile(pat)) for name, pat in AST_RULES]
    result = []
    for lineno, line in enumerate(code.splitlines(), 1):
        node = "Stmt/Expr"
        for name, pat in compiled:
            if pat.search(line):
                node = name
                break
        result.append({'line': lineno, 'code': line.rstrip(), 'node': node})
    return jsonify({'nodes': result})

if __name__ == '__main__':
    print("\n  AI Compiler Tutor - Web Server")
    print("  ----------------------------------")
    print("  Open in browser: http://localhost:5000")
    print("  Press Ctrl+C to stop\n")
    app.run(debug=False, host='0.0.0.0', port=5000)
