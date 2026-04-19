import subprocess
import os
import time
import platform

def run_with_timeout(c_file, timeout_sec=2.0):
    """
    Compiles and runs a C file with a strict timeout to detect infinite loops.
    Returns: (status, output)
    Statuses: "SUCCESS", "COMPILE_ERROR", "TIMEOUT" (Infinite Loop), "RUNTIME_ERROR"
    """
    base_name = os.path.splitext(os.path.basename(c_file))[0]
    exe_name = f"{base_name}.exe" if platform.system() == "Windows" else f"./{base_name}"
    
    # 1. Compile
    compile_cmd = ["gcc", c_file, "-o", base_name]
    try:
        subprocess.run(compile_cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        return "COMPILE_ERROR", e.stderr

    # 2. Run with timeout
    try:
        start_time = time.time()
        # On Windows, we don't have setsid, but timeout works fine
        result = subprocess.run([exe_name], capture_output=True, text=True, timeout=timeout_sec)
        duration = time.time() - start_time
        return "SUCCESS", result.stdout
    except subprocess.TimeoutExpired:
        return "TIMEOUT", f"Execution exceeded {timeout_sec}s. Potential Infinite Loop detected!"
    except Exception as e:
        return "RUNTIME_ERROR", str(e)
    finally:
        # Cleanup
        if os.path.exists(exe_name):
            try:
                os.remove(exe_name)
            except:
                pass

if __name__ == "__main__":
    # Test with a simple C file if provided
    import sys
    if len(sys.argv) > 1:
        status, output = run_with_timeout(sys.argv[1])
        print(f"Status: {status}")
        print(f"Output:\n{output}")
