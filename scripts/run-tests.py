from pathlib import Path
import subprocess
import minify_html
import sys
import argparse


ROOT_DIR = Path(__file__).parent.parent
TEST_DIR = ROOT_DIR / 'test'
EXEC = TEST_DIR.parent / 'src' / 'main.py'

def minify(s: str):
    return minify_html.minify(
        s,
        keep_html_and_head_opening_tags = True,
        minify_css = True,
    )

def print_success(dir: Path):
    id = dir.relative_to(TEST_DIR / 'cases')
    print(f"Test '{id}' - SUCCESS")

def print_fail(dir: Path):
    id = dir.relative_to(TEST_DIR / 'cases')
    print(f"Test '{id}' - FAIL")

def popen(dir: Path):
    input_file = dir / 'main.htmlp'
    return subprocess.Popen(
        ['python', EXEC, '--include-dir', dir, input_file],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

def expect(expected: str, dir: Path):
    test = popen(dir)
    process_out, process_err = test.communicate()
    expected = minify(expected)
    actual = minify(process_out.decode(sys.stdout.encoding))
    if (test.returncode == 0) and (actual == expected):
        print_success(dir)
        return
    print_fail(dir)
    if test.returncode == 0:
        print('Expected:')
        print(expected)
        print('Instead get:')
        print(actual)
    else:
        print('Test failed with error. Stderr:')
        print(process_err.decode(sys.stderr.encoding))
    print()

def expect_error(dir: Path):
    test = popen(dir)
    process_out, _ = test.communicate()
    if test.returncode != 0:
        print_success(dir)
        return
    output = process_out.decode(sys.stdout.encoding)
    print_fail(dir)
    print('Expected error but it has generated something:')
    print(output)
    print()

def run_single_case(dir: Path):
    try:
        with open(dir / 'expected_output.html') as file:
            expected = file.read()
        return expect(expected, dir)
    except FileNotFoundError:
        return expect_error(dir)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Doing something')
    parser.add_argument(
		'case', 
		type=str,
		nargs='?',
		help='Test case folder name if only single needed'
	)
    cases: Path = TEST_DIR / 'cases'
    test_case = parser.parse_args().case
    if test_case is not None:
        path: Path = cases / test_case
        if not path.exists():
            raise Exception(f"Test case '{test_case}' not found.")
        run_single_case(path)
            
    else:
        for test_case in cases.iterdir():
            run_single_case(test_case)
    