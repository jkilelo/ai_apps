"""
UTF-8 Runner for Custom Tools
Ensures proper UTF-8 encoding for the entire Python environment
"""

import sys
import os
import io
import locale
import codecs

# Force UTF-8 encoding at multiple levels
def force_utf8():
    """Force UTF-8 encoding throughout Python environment"""

    # 1. Set environment variables BEFORE any imports
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['PYTHONUTF8'] = '1'
    os.environ['LC_ALL'] = 'en_US.UTF-8'
    os.environ['LANG'] = 'en_US.UTF-8'
    os.environ['PYTHONLEGACYWINDOWSFSENCODING'] = '0'

    # 2. Force sys streams to UTF-8
    if sys.platform == 'win32':
        # Windows-specific UTF-8 setup
        import _locale
        _locale._getdefaultlocale = (lambda *args: ['en_US', 'utf8'])

        # Reconfigure stdout/stderr with UTF-8
        sys.stdout = io.TextIOWrapper(
            sys.stdout.buffer,
            encoding='utf-8',
            errors='replace',
            newline='',
            line_buffering=True
        )
        sys.stderr = io.TextIOWrapper(
            sys.stderr.buffer,
            encoding='utf-8',
            errors='replace',
            newline='',
            line_buffering=True
        )
        sys.stdin = io.TextIOWrapper(
            sys.stdin.buffer,
            encoding='utf-8',
            errors='replace'
        )

    # 3. Set default encoding for open()
    try:
        # Python < 3.10
        import _bootlocale
        _bootlocale.getpreferredencoding = lambda do_setlocale=True: 'utf-8'
    except ImportError:
        # Python >= 3.10
        try:
            import _locale
            _locale._getdefaultlocale = lambda *args: ('en_US', 'utf-8')
        except:
            pass

    # 4. Force locale
    try:
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    except:
        try:
            locale.setlocale(locale.LC_ALL, 'C.UTF-8')
        except:
            pass

    # 5. Monkey-patch open to default to UTF-8
    import builtins
    original_open = builtins.open

    def utf8_open(file, mode='r', buffering=-1, encoding=None, *args, **kwargs):
        if encoding is None and 'b' not in mode:
            encoding = 'utf-8'
        return original_open(file, mode, buffering, encoding, *args, **kwargs)

    builtins.open = utf8_open

    # 6. Set Windows console code page to UTF-8
    if sys.platform == 'win32':
        import subprocess
        try:
            # Set console to UTF-8
            subprocess.run(['chcp', '65001'], shell=True, capture_output=True)
        except:
            pass

        # Windows API calls for console
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            # Set console output to UTF-8
            kernel32.SetConsoleOutputCP(65001)
            # Set console input to UTF-8
            kernel32.SetConsoleCP(65001)
        except:
            pass

    # 7. Print status BEFORE modifying filesystem encoding
    print("✅ UTF-8 encoding forced at all levels")
    print(f"   - stdout encoding: {sys.stdout.encoding}")
    print(f"   - stderr encoding: {sys.stderr.encoding}")
    print(f"   - stdin encoding: {sys.stdin.encoding}")
    print(f"   - filesystem encoding: {sys.getfilesystemencoding()}")
    print(f"   - default encoding: {locale.getpreferredencoding()}")


# Apply UTF-8 forcing BEFORE any other imports
force_utf8()

# Now import and run the test
if __name__ == "__main__":
    import asyncio
    from pathlib import Path

    # Add parent directory to path
    sys.path.append(str(Path(__file__).parent.parent))

    # Import test module
    from test_custom_tools import main

    # Run the test
    print("\n" + "="*60)
    print("Running Custom Tools Test with Forced UTF-8")
    print("="*60)

    asyncio.run(main())