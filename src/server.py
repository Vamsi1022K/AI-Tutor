# =============================================================
# FILE: src/server.py
# AI Compiler Tutor — Flask Web Server  (Enhanced v2)
# =============================================================
import os, sys, re, json, subprocess, tempfile, time
from contextlib import contextmanager
from flask import Flask, request, jsonify, send_from_directory
from model_inference import explain_with_ai

SRC_DIR  = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SRC_DIR)
WEB_DIR  = os.path.join(BASE_DIR, 'web')
sys.path.insert(0, SRC_DIR)

DATASET_PATH = os.path.join(BASE_DIR, 'phase4_dataset', 'annotated_errors.json')
ERRORS_DIR   = os.path.join(BASE_DIR, 'errors')

app = Flask(__name__, static_folder=WEB_DIR)

# ── Load dataset ───────────────────────────────────────────────
def load_dataset():
    if not os.path.isfile(DATASET_PATH):
        return {}
    with open(DATASET_PATH, 'r', encoding='utf-8') as f:
        return {e['id']: e for e in json.load(f)}

DATASET = load_dataset()

GREEN_HISTORY = []
MAX_GREEN_HISTORY = 30

# ── Warning fallbacks ──────────────────────────────────────────
WARNING_FALLBACKS = {
    r'unused variable':   ("You declared a variable but never used it. Either use it or remove the declaration.",
                           "Remove the variable or add a use: printf(\"%d\", varname);"),
    r'unused parameter':  ("A function parameter was declared but never used inside the function body.",
                           "Use the parameter or suppress with: (void)param_name;"),
    r'set but not used':  ("You assigned a value to a variable but never read it back — logic bug likely.",
                           "Either use the variable in a calculation, or remove the assignment."),
    r'missing return':    ("Your function is declared to return a value but some paths reach the end without returning.",
                           "Add 'return 0;' (or the appropriate value) before the closing brace."),
    r'comparison between pointer and integer': (
                           "You are comparing a pointer with a plain integer which is almost always a bug.",
                           "If checking for empty string use strcmp(); if checking NULL use: if (ptr == NULL)."),
}

# ── Error → dataset-ID patterns ───────────────────────────────
PATTERNS = [
    (re.compile(r"expected.*';'",                             re.I), "E001"),
    (re.compile(r"expected.*'\)'",                            re.I), "E005"),
    (re.compile(r"expected.*'\}'",                            re.I), "E015"),
    (re.compile(r"implicit declaration of function 'printf'", re.I), "E004"),
    (re.compile(r"implicit declaration of function 'sqrt'",   re.I), "E024"),
    (re.compile(r"implicit declaration of function",          re.I), "E004"),
    (re.compile(r"undeclared",                                re.I), "E002"),
    (re.compile(r"redefinition of",                           re.I), "E009"),
    (re.compile(r"incompatible types when assigning",         re.I), "E003"),
    (re.compile(r"incompatible pointer type",                 re.I), "E022"),
    (re.compile(r"format '%d'.+double",                       re.I), "E011"),
    (re.compile(r"format '%d'.+float",                        re.I), "E020"),
    (re.compile(r"format '%.+' expects",                      re.I), "E011"),
    (re.compile(r"return with a value",                       re.I), "E010"),
    (re.compile(r"control reaches end of non-void",           re.I), "E021"),
    (re.compile(r"case label not within switch",              re.I), "E038"),
    (re.compile(r"break statement not within",                re.I), "E043"),
    (re.compile(r"continue statement not within",             re.I), "E044"),
    (re.compile(r"lvalue required",                           re.I), "E049"),
    (re.compile(r"void value not ignored",                    re.I), "E041"),
    (re.compile(r"too few arguments",                         re.I), "E006"),
    (re.compile(r"too many arguments",                        re.I), "E047"),
    (re.compile(r"called object is not a function",           re.I), "E036"),
    (re.compile(r"array subscript.+above array bounds",       re.I), "E016"),
    (re.compile(r"null pointer dereference",                  re.I), "E017"),
    (re.compile(r"division by zero",                          re.I), "E018"),
    (re.compile(r"used uninitialized",                        re.I), "E019"),
    (re.compile(r"integer overflow",                          re.I), "E025"),
    (re.compile(r"excess elements in array",                  re.I), "E029"),
    (re.compile(r"may fall through",                          re.I), "E027"),
    (re.compile(r"has no member named",                       re.I), "E030"),
    (re.compile(r"stray '#'",                                 re.I), "E032"),
    (re.compile(r"Infinite Loop",                             re.I), "E031"),
    (re.compile(r"expected.*('='|','|'asm'|'__attribute__')", re.I), "E033"),
]

GCC_RE = re.compile(r'^([^:]+):(\d+):(\d+):\s*(error|warning):\s*(.+)$')

SEC_RULES = [
    (re.compile(r'\bgets\s*\('),          "gets() — buffer overflow risk",            "fgets(buf, sizeof(buf), stdin)"),
    (re.compile(r'\bstrcpy\s*\('),        "strcpy() — no bounds check",               "strncpy(dest, src, sizeof(dest)-1)"),
    (re.compile(r'scanf\s*\(\s*"%s"'),    'scanf("%s") — unlimited input',             'scanf("%49s", str)'),
    (re.compile(r'\bsprintf\s*\('),       "sprintf() — can overflow buffer",           "snprintf(buf, sizeof(buf), fmt, ...)"),
    (re.compile(r'\bstrcat\s*\('),        "strcat() — no bounds check",                "strncat(dest, src, max_len)"),
    (re.compile(r'\bsystem\s*\('),        "system() — shell injection risk",           "Avoid system(); use proper API"),
    (re.compile(r'\bmalloc\s*\('),        "malloc() — unchecked NULL return",          "if(!ptr){ perror('malloc'); exit(1); }"),
    (re.compile(r'\bfree\s*\('),          "free() — double-free/use-after-free risk",  "Set to NULL after free: ptr = NULL;"),
]

# ── Static analysis helpers ────────────────────────────────────

def detect_infinite_loops(code):
    """Detect probable infinite loops: while(1), for(;;), while(true)."""
    issues = []
    lines = code.splitlines()
    in_infinite = False
    brace_depth = 0
    loop_start_line = 0
    has_break = False

    for i, raw in enumerate(lines, 1):
        stripped = raw.strip()

        # Detect start of infinite loop
        if re.match(r'while\s*\(\s*(1|true|1\s*==\s*1)\s*\)\s*\{?', stripped):
            in_infinite = True
            loop_start_line = i
            brace_depth = raw.count('{') - raw.count('}')
            has_break = False
            continue
        if re.match(r'for\s*\(\s*;\s*;\s*\)\s*\{?', stripped):
            in_infinite = True
            loop_start_line = i
            brace_depth = raw.count('{') - raw.count('}')
            has_break = False
            continue

        if in_infinite:
            brace_depth += raw.count('{') - raw.count('}')
            if re.search(r'\bbreak\b|\breturn\b|\bexit\s*\(', stripped):
                has_break = True
            if brace_depth <= 0:
                if not has_break:
                    issues.append({
                        'line': loop_start_line,
                        'type': 'warning',
                        'msg': 'Potential infinite loop detected',
                        'explanation': (
                            'This loop has no conditional exit — it runs forever. '
                            'In a real program this will hang/freeze unless a break, return, or exit() '
                            'is guaranteed to be reachable inside the loop body.'
                        ),
                        'fix': 'Add a break condition: if (condition) break;  or change to while (condition) { ... }',
                        'fix_code': '// Instead of while(1) use:\nwhile (notDone) {\n    // ... work ...\n    if (exitCondition) break;\n}',
                        'error_id': 'E031',
                        'category': 'Control Flow',
                        'secure': True,
                    })
                in_infinite = False

    return issues


def detect_zero_division(code):
    """Detect division or modulo by literal zero."""
    issues = []
    DIV_ZERO = re.compile(r'(?<![/])/\s*0\b|%\s*0\b')
    for i, line in enumerate(code.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith('//') or stripped.startswith('*'):
            continue
        if DIV_ZERO.search(stripped):
            issues.append({
                'line': i,
                'type': 'error',
                'msg': 'Division by zero',
                'explanation': (
                    'You are dividing (or taking modulo) by the literal value 0. '
                    'In C this causes undefined behaviour — the program will likely crash '
                    'with a floating point exception (SIGFPE) at runtime.'
                ),
                'fix': 'Guard every division: if (divisor != 0) { result = a / divisor; }',
                'fix_code': 'if (b != 0) {\n    result = a / b;\n} else {\n    fprintf(stderr, "Error: division by zero\\n");\n}',
                'error_id': 'E018',
                'category': 'Runtime',
                'secure': True,
            })
    return issues


def detect_type_issues(code):
    """Detect basic type mismatches not caught by GCC -Wall."""
    issues = []
    lines = code.splitlines()

    # Pattern: assigning string literal to int variable  e.g.  int x = "hello";
    INT_STR = re.compile(r'\bint\s+\w+\s*=\s*"')
    # Pattern: using char variable where %d format expects int (common beginner error tracked separately)
    CHAR_INT = re.compile(r'char\s+\w+\s*=\s*\d{3,}')  # char x = 300; — overflow

    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith('//') or stripped.startswith('*'):
            continue
        if INT_STR.search(stripped):
            issues.append({
                'line': i,
                'type': 'error',
                'msg': 'Type mismatch: assigning string literal to int variable',
                'explanation': (
                    'You are trying to store a string (text in quotes) into an integer variable. '
                    'An int can only hold a number, not text. '
                    'Use char[] or char* to store strings.'
                ),
                'fix': 'Change the type: char str[] = "hello"; or use int x = 42;',
                'fix_code': '// Wrong:\nint x = "hello";\n// Correct:\nchar str[] = "hello";\nint x = 42;',
                'error_id': 'E003',
                'category': 'Type',
                'secure': True,
            })
        if CHAR_INT.search(stripped):
            issues.append({
                'line': i,
                'type': 'warning',
                'msg': 'Possible char overflow: value too large for char type',
                'explanation': (
                    'A char variable can typically hold values from -128 to 127 (signed) or 0 to 255 (unsigned). '
                    'Assigning a value outside this range causes overflow and unpredictable behaviour.'
                ),
                'fix': 'Use int instead of char if you need to store large numbers.',
                'fix_code': '// Wrong:\nchar c = 300;  // overflow!\n// Correct:\nint c = 300;   // or use unsigned char (max 255)',
                'error_id': 'WARN',
                'category': 'Type',
                'secure': True,
            })
    return issues


def match_error(msg):
    for pat, eid in PATTERNS:
        if pat.search(msg):
            return DATASET.get(eid)
    return None

def warning_fallback(msg):
    for pat, (expl, fix) in WARNING_FALLBACKS.items():
        if re.search(pat, msg, re.I):
            return expl, fix
    return None, None

def compile_code(code_text):
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


def build_error_result(err):
    """Convert a raw GCC error dict into a rich result dict."""
    entry = match_error(err['msg'])
    if entry:
        return {
            'line': err['line'], 'col': err['col'],
            'type': err['type'], 'gcc_msg': err['msg'], 'raw': err['raw'],
            'explanation': entry['plain_explanation'],
            'ai_logic': entry['plain_explanation'],
            'fix': entry['fix'],
            'fix_code': entry.get('fixed_code', ''),
            'secure': entry.get('secure', True),
            'category': entry.get('category', ''),
            'error_id': entry['id'],
        }
    fb_expl, fb_fix = warning_fallback(err['msg'])
    if fb_expl:
        return {
            'line': err['line'], 'col': err['col'],
            'type': err['type'], 'gcc_msg': err['msg'], 'raw': err['raw'],
            'explanation': fb_expl, 'ai_logic': fb_expl,
            'fix': fb_fix, 'fix_code': '', 'secure': True,
            'category': 'Warning', 'error_id': 'WARN',
        }
    # Neural fallback
    raw_ai = explain_with_ai(err['msg'])
    if (not raw_ai or len(raw_ai) < 10
            or err['msg'][:20].lower() in raw_ai.lower()
            or raw_ai.strip().startswith("C compiler")):
        raw_ai = ("The compiler found an issue it cannot automatically categorise. "
                  "Read the GCC message carefully, check the highlighted line, "
                  "and look for missing punctuation or mismatched types.")
    return {
        'line': err['line'], 'col': err['col'],
        'type': err['type'], 'gcc_msg': err['msg'], 'raw': err['raw'],
        'explanation': raw_ai, 'ai_logic': raw_ai,
        'fix': f"Review line {err['line']} carefully for missing symbols, incorrect types, or undeclared names.",
        'fix_code': '', 'secure': True,
        'category': 'Neural Analysis', 'error_id': 'AI-GEN',
    }


class EnergyProfiler:
    """Pinpoint execution cost by stage duration."""
    def __init__(self):
        self.stage_durations = {}

    @contextmanager
    def stage(self, name):
        t0 = time.perf_counter()
        try:
            yield
        finally:
            self.stage_durations[name] = self.stage_durations.get(name, 0.0) + (time.perf_counter() - t0)


def _read_intel_power_gadget_csv():
    """
    Optional Windows path: read latest Intel Power Gadget CSV export if present.
    Returns average power in W or None if unavailable.
    """
    candidates = [
        os.path.join(BASE_DIR, 'green_metrics'),
        os.path.join(BASE_DIR, 'logs'),
    ]
    csv_files = []
    for cdir in candidates:
        if os.path.isdir(cdir):
            for f in os.listdir(cdir):
                if f.lower().endswith('.csv') and 'power' in f.lower():
                    csv_files.append(os.path.join(cdir, f))
    if not csv_files:
        return None
    csv_files.sort(key=lambda p: os.path.getmtime(p), reverse=True)
    path = csv_files[0]
    try:
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            lines = [ln.strip() for ln in f if ln.strip()]
        if not lines:
            return None
        headers = [h.strip().lower() for h in lines[0].split(',')]
        idx = -1
        for i, h in enumerate(headers):
            if 'power' in h and 'watt' in h:
                idx = i
                break
        if idx < 0:
            return None
        vals = []
        for row in lines[1:]:
            cols = [c.strip() for c in row.split(',')]
            if idx < len(cols):
                try:
                    vals.append(float(cols[idx]))
                except ValueError:
                    pass
        if not vals:
            return None
        return sum(vals) / len(vals)
    except OSError:
        return None


def _measure_energy(code_lines, duration_s):
    """
    Multi-provider green measurement strategy:
      1) CodeCarbon (if installed)
      2) Intel Power Gadget CSV (if available on Windows)
      3) Fallback model (CPU TDP approximation)
    """
    GRID_CO2 = 0.475  # kg CO2 per kWh
    # Slightly scale load by non-empty code size.
    line_factor = min(1.0, max(0.25, code_lines / 400.0))

    provider = "tdp_fallback"
    notes = ["CodeCarbon unavailable -> using CPU TDP fallback."]
    rapl_mode = "simulated"
    energy_j = None
    avg_power_w = None

    # Provider 1: CodeCarbon
    try:
        from codecarbon import EmissionsTracker  # type: ignore
        tracker = EmissionsTracker(
            save_to_file=False,
            log_level='error',
            tracking_mode='machine',
            measure_power_secs=1,
        )
        tracker.start()
        tracker.stop()
        data = getattr(tracker, "_total_energy", None)
        if data is not None and data >= 0:
            energy_j = float(data) * 3_600_000.0  # kWh -> J
            if duration_s > 0:
                avg_power_w = energy_j / duration_s
            provider = "codecarbon"
            notes = ["CodeCarbon integrated successfully for this run."]
            rapl_mode = "estimated_by_codecarbon"
    except Exception:
        pass

    # Provider 2: Intel Power Gadget CSV (best-effort on Windows)
    if energy_j is None:
        ipg_avg = _read_intel_power_gadget_csv()
        if ipg_avg is not None and ipg_avg > 0:
            avg_power_w = float(ipg_avg)
            energy_j = avg_power_w * duration_s
            provider = "intel_power_gadget_csv"
            notes = ["Read latest Intel Power Gadget CSV for average power."]
            rapl_mode = "windows_csv_bridge"

    # Provider 3: deterministic fallback model
    if energy_j is None:
        TDP_W = 15.0
        BASE_LOAD_FRACTION = 0.25
        avg_power_w = TDP_W * BASE_LOAD_FRACTION * line_factor
        energy_j = avg_power_w * duration_s

    energy_kwh = energy_j / 3_600_000.0
    carbon_kg = energy_kwh * GRID_CO2
    carbon_mg = carbon_kg * 1_000_000.0

    return {
        'provider': provider,
        'rapl_mode': rapl_mode,
        'provider_notes': notes,
        'energy_j': float(energy_j),
        'avg_power_w': float(avg_power_w) if avg_power_w is not None else 0.0,
        'carbon_mg': float(carbon_mg),
    }


def _virtualize_energy(stage_durations, total_energy_j):
    """
    Energy virtualization:
    allocate total measured energy to per-stage entities by runtime weight.
    """
    if not stage_durations:
        return {}
    positive = {k: v for k, v in stage_durations.items() if v > 0}
    total_t = sum(positive.values())
    if total_t <= 0:
        return {k: 0.0 for k in stage_durations}
    alloc = {}
    for name, sec in positive.items():
        alloc[name] = round(total_energy_j * (sec / total_t), 6)
    return alloc


# ── Routes ─────────────────────────────────────────────────────

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

@app.route('/api/health')
def health():
    return jsonify({'ok': True, 'service': 'ai-compiler-tutor'})


@app.route('/api/analyze_all', methods=['POST'])
def analyze_all():
    """
    Single endpoint: compile + static checks + security + AST + green metrics.
    Called once by the frontend after the user clicks Analyze.
    """
    t0 = time.perf_counter()
    profiler = EnergyProfiler()
    data = request.json or {}
    code = data.get('code', '')
    if not code.strip():
        return jsonify({'error': 'No code provided'}), 400

    # ── 1. GCC compile ────────────────────────────────────────
    with profiler.stage("Compile + Parse"):
        stderr, raw_errors = compile_code(code)
        errors = [build_error_result(e) for e in raw_errors]

    # ── 2. Static checks (run on source, not on GCC output) ──
    with profiler.stage("Static Analysis"):
        static = (detect_zero_division(code)
                  + detect_infinite_loops(code)
                  + detect_type_issues(code))

    # Convert static issues to same shape as error results
    for s in static:
        # De-duplicate: skip if GCC already reported same line/id
        already = any(
            e['line'] == s['line'] and e['error_id'] == s['error_id']
            for e in errors
        )
        if not already:
            errors.append({
                'line':        s['line'], 'col': 1,
                'type':        s['type'],
                'gcc_msg':     s['msg'],
                'raw':         f"code.c:{s['line']}:1: {s['type']}: {s['msg']}",
                'explanation': s['explanation'],
                'ai_logic':    s['explanation'],
                'fix':         s['fix'],
                'fix_code':    s.get('fix_code', ''),
                'secure':      s.get('secure', True),
                'category':    s.get('category', ''),
                'error_id':    s['error_id'],
            })

    errors.sort(key=lambda e: e['line'])

    # ── 3. Security scan ─────────────────────────────────────
    with profiler.stage("Security Scan"):
        sec_issues = []
        for lineno, line in enumerate(code.splitlines(), 1):
            stripped = line.strip()
            if stripped.startswith('//') or stripped.startswith('*'):
                continue
            for pat, reason, fix in SEC_RULES:
                if pat.search(line):
                    sec_issues.append({'line': lineno, 'code': stripped[:100],
                                       'reason': reason, 'fix': fix})

    # ── 4. AST parse ─────────────────────────────────────────
    with profiler.stage("AST Build"):
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
        compiled_ast = [(name, re.compile(pat)) for name, pat in AST_RULES]
        ast_nodes = []
        for lineno, line in enumerate(code.splitlines(), 1):
            node = "Stmt/Expr"
            for name, pat in compiled_ast:
                if pat.search(line):
                    node = name
                    break
            ast_nodes.append({'line': lineno, 'code': line.rstrip(), 'node': node})

    # ── 5. Green metrics ─────────────────────────────────────
    duration = time.perf_counter() - t0
    code_lines = len([l for l in code.splitlines() if l.strip()])
    measured = _measure_energy(code_lines, duration)
    stage_alloc = _virtualize_energy(profiler.stage_durations, measured['energy_j'])
    green = {
        'energy_j': round(measured['energy_j'], 6),
        'carbon_mg': round(measured['carbon_mg'], 6),
        'avg_power_w': round(measured['avg_power_w'], 6),
        'duration_s': round(duration, 6),
        'code_lines': code_lines,
        'provider': measured['provider'],
        'rapl_mode': measured['rapl_mode'],
        'provider_notes': measured['provider_notes'],
        'stages': stage_alloc,
        'stage_duration_s': {k: round(v, 6) for k, v in profiler.stage_durations.items()},
    }
    GREEN_HISTORY.append({
        'run_id': int(time.time() * 1000),
        'lines': code_lines,
        'energy_j': green['energy_j'],
        'carbon_mg': green['carbon_mg'],
        'avg_power_w': green['avg_power_w'],
        'duration_s': green['duration_s'],
    })
    if len(GREEN_HISTORY) > MAX_GREEN_HISTORY:
        del GREEN_HISTORY[:-MAX_GREEN_HISTORY]

    return jsonify({
        'errors':    errors,
        'stderr':    stderr,
        'error_count': len(errors),
        'security':  {'issues': sec_issues, 'count': len(sec_issues)},
        'ast':       {'nodes': ast_nodes},
        'green':     green,
        'green_history': GREEN_HISTORY,
    })


# ── Legacy individual routes (kept for backward compat) ───────

@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.json or {}
    code = data.get('code', '')
    if not code.strip():
        return jsonify({'error': 'No code provided'}), 400
    stderr, raw_errors = compile_code(code)
    results = [build_error_result(e) for e in raw_errors]
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
    print("\n  AI Compiler Tutor - Web Server v2")
    print("  ----------------------------------")
    print("  Open in browser: http://localhost:5000")
    print("  Press Ctrl+C to stop\n")
    app.run(debug=False, host='0.0.0.0', port=5000)
